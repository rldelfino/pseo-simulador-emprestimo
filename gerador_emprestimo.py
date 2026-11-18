"""Gera o site estático do simulador de empréstimo via cartão de crédito ("Pix no cartão").

Saída em paginas_seo/ (publicada no Cloudflare Pages). O CSS vem do Tailwind (npm run build:css).
Uso: python gerador_emprestimo.py [pasta_de_saida]

Regras do projeto: poucas páginas, cada uma com conteúdo próprio (nada de grade de páginas quase idênticas);
nenhum dado pessoal; medição só com Umami (sem cookies). O texto das páginas fica em conteudo.py.

Páginas por valor (R$ 500 a R$ 5.000) NÃO são geradas: seriam quase iguais à home (o Google recusou esse padrão nos outros
simuladores). Se um dia tiverem conteúdo próprio, ligue PAGINAS_VALOR_INDEXAVEIS (hoje não existe gerador para elas).
"""
import datetime
import hashlib
import json
import os
import re
import shutil
import sys

import calculo
import conteudo
import dados_abertos
import feed_atom
import indexnow
import layout
import taxas_referencia

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA_PADRAO = os.path.join(AQUI, "paginas_seo")

DOMINIO = "https://emprestimo.datalabglobal.com"
HUB = "https://www.datalabglobal.com"
UMAMI_ID = "ba3c0b88-59e8-47dd-866d-0b05e5e7dae9"
RAZAO_SOCIAL = "Satori Soluções Comerciais LTDA"
CNPJ = "63.998.502/0001-73"
EMAIL = "contato@datalabglobal.com"
PAGINAS_VALOR_INDEXAVEIS = False

# Data de atualização de cada página: só muda quando o conteúdo muda (ver _datas_das_paginas). O arquivo fica no repositório
# e o robô semanal o commita junto com as páginas.
MANIFESTO_PADRAO = os.path.join(AQUI, "dados", "datas_paginas.json")
DATA_SENTINELA = datetime.date(2000, 1, 1)

HOME_TITLE = "Pix no cartão de crédito: simule parcela, IOF e CET"
HOME_DESC = ("Simule o Pix no cartão de crédito (R$ 300 a R$ 5.000, em 2x a 12x) e veja parcela, total na fatura, IOF e CET antes de contratar. "
             "Crédito caro: confira o custo.")

# Páginas indexáveis (entram no sitemap): home + as de conteudo.PAGINAS.
PAGINAS_INDEXAVEIS = ["/"] + ["/" + pg["slug"] for pg in conteudo.PAGINAS]

CSP = (
    "default-src 'self'; "
    "script-src 'self' https://static.cloudflareinsights.com https://cloud.umami.is; "
    "style-src 'self'; "
    "img-src 'self' data:; "
    "font-src 'self'; "
    "connect-src 'self' https://api.triagem.digital https://cloudflareinsights.com https://cloud.umami.is https://gateway.umami.is; "
    "frame-ancestors 'none'; base-uri 'self'; form-action 'self'; object-src 'none'; upgrade-insecure-requests"
)

HEADERS = """/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Strict-Transport-Security: max-age=31536000; includeSubDomains
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: geolocation=(), camera=(), microphone=(), payment=(), usb=(), interest-cohort=()
  Cross-Origin-Opener-Policy: same-origin
  Content-Security-Policy: @@CSP@@

/styles.css
  Cache-Control: public, max-age=31536000, immutable

/calculo.js
  Cache-Control: public, max-age=3600, must-revalidate

/simulador.js
  Cache-Control: public, max-age=3600, must-revalidate

/menu.js
  Cache-Control: public, max-age=3600, must-revalidate

/logo-header.webp
  Cache-Control: public, max-age=86400, must-revalidate

/og-image.png
  Cache-Control: public, max-age=86400, must-revalidate

/logo-full.png
  Cache-Control: public, max-age=86400, must-revalidate

/fonts/*
  Cache-Control: public, max-age=31536000, immutable
"""

CALCULO_JS = """/* GERADO por gerador_emprestimo.py a partir de dados/pix-tabela-esperada.json. Não edite à mão.
   Mesma conta de calculo.py (os testes comparam os dois). */
(function (root) {
  'use strict';
  var T = @@TABELA@@;
  var PIX_MIN = @@PIX_MIN@@;
  var PIX_MAX = T.pix_max;
  // Taxas médias de juros do Banco Central (referência, não oferta): aa = ao ano, am = ao mês equivalente (juros compostos).
  var REF = @@REFERENCIAS@@;

  function simular(modo, valor, limite, parcelas) {
    var fator = T.fator_base + T.fator_por_parcela * parcelas;
    var pix = modo === 'valor' ? valor : Math.min(limite / (1 + fator), PIX_MAX);
    var total = pix * (1 + fator);
    var cet = T.cet[String(parcelas)];
    return {
      pix: pix,
      total: total,
      parcela: total / parcelas,
      iof: pix * (T.iof_fixo + T.iof_por_parcela * parcelas),
      jurosMes: cet.monthly,
      cetAno: cet.annual
    };
  }

  function brl(v) { return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v); }
  function pct(v) { return v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + '%'; }

  var api = { simular: simular, brl: brl, pct: pct, PIX_MIN: PIX_MIN, PIX_MAX: PIX_MAX, tableUUID: T.table_uuid, tabela: T, referencias: REF };
  root.DatalabPix = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);
"""


NOT_FOUND = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Página não encontrada</title>
<meta name="robots" content="noindex">
<link rel="stylesheet" href="/styles.css">
</head>
<body>
<main class="mx-auto max-w-xl px-4 py-24 text-center">
  <h1 class="text-3xl font-extrabold">Página não encontrada</h1>
  <p class="mt-3 text-slate-300">O endereço não existe mais ou foi digitado errado.</p>
  <p class="mt-6"><a class="inline-flex min-h-11 items-center underline" href="/">Voltar ao simulador do Pix no cartão</a></p>
</main>
</body>
</html>
"""

LLMS = """# Pix no cartão de crédito (Datalab Global)

> Simulador gratuito do Pix no cartão de crédito: você recebe um Pix de R$ 300 a R$ 5.000 e paga em 2x a 12x na fatura. Mostra parcela, total na fatura, IOF e CET antes de qualquer contratação. É crédito caro.

- Responsável: @@RAZAO@@, CNPJ @@CNPJ@@
- Atualizado em @@ATUALIZADO@@
- Fonte dos números: Tabela 10 do parceiro (correspondente bancário), conferida toda semana pela API do próprio parceiro.
- Conta: fator = 0,5479 + 0,003 x parcelas; parcela = valor x (1 + fator) / parcelas; IOF = valor x (0,0038 + 0,00246 x parcelas).
- A aprovação depende de análise de crédito. A simulação não é proposta de crédito. A Datalab Global pode receber comissão do parceiro.
- Dados abertos (CSV e JSON): @@DOMINIO@@/dados-abertos. Tabela 10 em CC BY 4.0; séries do Banco Central em ODbL 1.0.
- Feed Atom: @@DOMINIO@@/feed.xml

## Páginas
@@LISTA@@
"""


def _preencher(texto, valores):
    for chave, valor in valores.items():
        texto = texto.replace("@@" + chave + "@@", valor)
    return texto


def referencias_bcb():
    """Última taxa média do BCB de cada série, para o simulador comparar com os juros do Pix. Sem dado, lista vazia (o bloco some)."""
    linhas = taxas_referencia.ler()
    saida = []
    for sr in taxas_referencia.SERIES:
        u = taxas_referencia.ultima(sr["codigo"], linhas)
        if u:
            saida.append({"chave": sr["chave"], "nome": sr["nome"], "mes": taxas_referencia.mes_extenso(u["mes"]),
                          "aa": u["taxa_aa"], "am": round(taxas_referencia.mensal_equivalente(u["taxa_aa"]), 4)})
    return saida


def gerar_calculo_js():
    tabela = json.dumps(calculo.TABELA, ensure_ascii=False, sort_keys=True)
    refs = json.dumps(referencias_bcb(), ensure_ascii=False, sort_keys=True)
    return _preencher(CALCULO_JS, {"TABELA": tabela, "PIX_MIN": str(calculo.PIX_MIN), "REFERENCIAS": refs})


def _resumo(dados):
    return hashlib.sha256(dados).hexdigest()[:10]


def versao_simulador_js():
    with open(os.path.join(AQUI, "src", "simulador.js"), "rb") as f:
        return _resumo(f.read())


def versao_menu_js():
    with open(os.path.join(AQUI, "src", "menu.js"), "rb") as f:
        return _resumo(f.read())


def menu_script():
    return '<script defer src="/menu.js?v=' + versao_menu_js() + '"></script>\n'


def versao_calculo_js():
    return _resumo(gerar_calculo_js().encode("utf-8"))


def home_scripts():
    """Os scripts também têm a versão no endereço: o Cloudflare guarda .js na borda por horas e ignora o max-age do _headers; com ?v=<resumo>
    o endereço muda junto com o conteúdo e ninguém recebe HTML novo com JS velho."""
    return ('<script src="/calculo.js?v=' + versao_calculo_js() + '"></script>\n'
            '<script src="/simulador.js?v=' + versao_simulador_js() + '"></script>\n' + menu_script())


def versao_css():
    """Resumo do styles.css compilado. O arquivo tem cache de 1 ano e imutável; a versão no endereço (?v=) faz o navegador buscar o novo
    quando o CSS muda. Fluxo: gerar -> npm run build:css -> gerar de novo (a segunda rodada só atualiza esta versão)."""
    caminho = os.path.join(AQUI, "paginas_seo", "styles.css")
    if not os.path.exists(caminho):
        return "0"
    with open(caminho, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:10]


def versao_icones():
    """Resumo do logo e dos ícones. Sem a versão na URL, quem já visitou continuaria vendo o logo/ícone antigo pelo cache (o logo mudou de verde para roxo)."""
    h = hashlib.sha256()
    for nome in ("logo-full.png", "favicon.ico", "favicon-32.png", "apple-touch-icon.png"):
        with open(os.path.join(AQUI, "paginas_seo", nome), "rb") as f:
            h.update(f.read())
    return h.hexdigest()[:10]


def versao_og_image():
    """A imagem de compartilhamento muda de endereço (?v=) quando muda o arquivo: Facebook, WhatsApp e LinkedIn guardam a antiga por semanas."""
    with open(os.path.join(AQUI, "paginas_seo", "og-image.png"), "rb") as f:
        return _resumo(f.read())


def _sem_tags(html):
    return re.sub(r"<[^>]+>", "", html).replace("&quot;", '"')


def _ld(dados):
    return '<script type="application/ld+json">' + json.dumps(dados, ensure_ascii=False) + "</script>\n"


# Navegação: poucos links no cabeçalho, tudo no menu do celular e no rodapé (em colunas).
DESTAQUES = ["como-funciona", "custo-cet-iof", "e-seguro-golpes", "taxas-de-referencia"]
ENTENDA = ["como-funciona", "e-seguro-golpes", "custo-cet-iof", "pix-no-cartao-ou-outro-credito", "quando-nao-vale-a-pena"]
TRANSPARENCIA = ["taxas-de-referencia", "metodologia", "dados-abertos", "atualizacoes", "sobre"]
LEGAL = ["privacidade", "termos"]
ROTULOS = {"atualizacoes": "Atualizações", "dados-abertos": "Dados abertos", "privacidade": "Privacidade", "termos": "Termos de uso",
           "pix-no-cartao-ou-outro-credito": "Comparar com outros créditos", "taxas-de-referencia": "Taxas do Banco Central",
           "custo-cet-iof": "CET e IOF", "e-seguro-golpes": "É seguro? Golpes", "quando-nao-vale-a-pena": "Quando não vale a pena"}


def _pg(slug):
    return next(pg for pg in conteudo.PAGINAS if pg["slug"] == slug)


def _rotulo(slug):
    return ROTULOS.get(slug) or _pg(slug).get("menu") or _pg(slug)["h1"]


def _nav_desktop():
    return "".join('<a class="hover:text-white" href="/' + s + '">' + (_pg(s).get("menu") or _rotulo(s)) + "</a>" for s in DESTAQUES)


def _nav_celular():
    links = ENTENDA + [s for s in TRANSPARENCIA if s not in ENTENDA]
    return "".join('<a class="flex min-h-11 items-center rounded-lg px-3 hover:bg-white/5" href="/' + s + '">' + _rotulo(s) + "</a>" for s in links)


def _lista_rodape(slugs, extra=""):
    return "".join('<li><a class="inline-flex min-h-11 items-center hover:text-white md:min-h-8" href="/' + s + '">' + _rotulo(s) + "</a></li>" for s in slugs) + extra


# Os outros simuladores da Datalab Global (outros produtos, outros subdomínios). O texto do link descreve o destino.
OUTROS_SIMULADORES = [
    ("https://simulador.datalabglobal.com/", "Financiamento imobiliário"),
    ("https://veiculos.datalabglobal.com/", "Financiamento de veículos"),
    ("https://homeequity.datalabglobal.com/", "Crédito com imóvel em garantia (Home Equity)"),
    (HUB + "/", "Datalab Global"),
]


def _lista_outros():
    return "".join('<li><a class="inline-flex min-h-11 items-center hover:text-white md:min-h-8" href="' + url + '">' + texto + "</a></li>"
                   for url, texto in OUTROS_SIMULADORES)


def _faq_html():
    saida = ""
    for pergunta, resposta in conteudo.FAQ:
        saida += ('<details class="faq rounded-2xl border border-white/10 bg-slate-900/40 p-5"><summary class="flex min-h-11 cursor-pointer items-center justify-between gap-4 font-semibold text-white">'
                  + pergunta + '<span class="mais text-xl text-slate-400" aria-hidden="true">+</span></summary><p class="mt-3 text-sm leading-relaxed text-slate-300">'
                  + resposta + "</p></details>")
    return saida


def _cartoes_html():
    saida = ""
    for pg in conteudo.PAGINAS:
        if not pg.get("menu"):
            continue
        saida += ('<a href="/' + pg["slug"] + '" class="glass-panel block rounded-2xl p-6 hover:border-violet-400/40"><span class="font-serif text-lg font-bold text-white">'
                  + pg["menu"] + '</span><span class="mt-2 block text-sm leading-relaxed text-slate-400">' + pg["desc"]
                  + '</span><span class="mt-4 block text-xs font-bold uppercase tracking-widest text-violet-400">Ler &rarr;</span></a>')
    return saida


def _ctx(hoje):
    return {
        "razao": RAZAO_SOCIAL, "cnpj": CNPJ, "email": EMAIL, "atualizado": hoje.strftime("%d/%m/%Y"),
        "atualizacoes": conteudo.ATUALIZACOES,
    }


def _organizacao():
    return {"@type": "Organization", "@id": DOMINIO + "/#organizacao", "name": "Datalab Global", "legalName": RAZAO_SOCIAL,
            "taxID": CNPJ, "url": HUB + "/", "email": EMAIL}


def _pagina_home(valores, hoje):
    faq = {"@context": "https://schema.org", "@type": "FAQPage",
           "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": _sem_tags(r)}} for q, r in conteudo.FAQ]}
    site = {"@context": "https://schema.org", "@graph": [
        _organizacao(),
        {"@type": "WebSite", "@id": DOMINIO + "/#site", "url": DOMINIO + "/", "name": "Pix no cartão — Datalab Global", "inLanguage": "pt-BR",
         "publisher": {"@id": DOMINIO + "/#organizacao"}},
    ]}
    main = _preencher(layout.HOME_MAIN, dict(valores, ROTULO=layout.ROTULO, CARTOES=_cartoes_html(), FAQ=_faq_html(), COMPARA=conteudo.frase_home()))
    return _preencher(layout.LAYOUT, dict(valores, TITLE=HOME_TITLE, DESC=HOME_DESC, CANONICAL=DOMINIO + "/", ROBOTS="index,follow,max-image-preview:large",
                                          OGTYPE="website", JSONLD=_ld(site) + _ld(faq), MAIN=main, SCRIPTS=home_scripts()))


def _pagina_guia(pg, valores, hoje, ctx):
    canonical = DOMINIO + "/" + pg["slug"]
    corpo = pg["corpo"](ctx)
    guia = pg.get("guia", True)
    rotulo_pagina = pg.get("menu") or _rotulo(pg["slug"])
    cabecalho = _preencher(layout.GUIA_CABECALHO, dict(valores, ROTULO_PAGINA=rotulo_pagina, H1=pg["h1"]))
    if guia:
        outros = [x for x in conteudo.PAGINAS if x.get("menu") and x["slug"] != pg["slug"]]
        i = next((k for k, x in enumerate(outros) if conteudo.PAGINAS.index(x) > conteudo.PAGINAS.index(pg)), 0)
        relacionados = (outros[i:] + outros[:i])[:3]
        rel = "".join('<li><a class="glass-panel block rounded-2xl p-4 text-sm font-semibold leading-snug text-white hover:border-violet-400/40" href="/'
                      + x["slug"] + '">' + x["h1"] + "</a></li>" for x in relacionados)
        fecho = _preencher(layout.GUIA_FECHO, {"RELACIONADOS": rel})
    else:
        fecho = ""
    main = cabecalho + corpo + layout.GUIA_MEIO + fecho + "</article>"
    artigo = {"@context": "https://schema.org", "@type": "Article", "headline": pg["h1"], "description": pg["desc"], "inLanguage": "pt-BR",
              "dateModified": hoje.isoformat(), "mainEntityOfPage": canonical,
              "author": {"@type": "Organization", "name": "Datalab Global"}, "publisher": _organizacao()}
    ld = _ld(artigo) if guia else ""
    return _preencher(layout.LAYOUT, dict(valores, TITLE=pg["title"], DESC=pg["desc"], CANONICAL=canonical, ROBOTS="index,follow,max-image-preview:large",
                                          OGTYPE="article" if guia else "website", JSONLD=ld, MAIN=main, SCRIPTS=menu_script()))


def _ler_manifesto(caminho):
    if not caminho:
        return {}
    try:
        with open(caminho, encoding="utf-8") as f:
            dados = json.load(f)
    except (OSError, ValueError):
        return {}
    return dados if isinstance(dados, dict) else {}


def _gravar_manifesto(caminho, dados):
    texto = json.dumps(dados, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    try:
        with open(caminho, encoding="utf-8", newline="") as f:
            if f.read() == texto:
                return
    except OSError:
        pass
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)


def _impressao(html):
    """Resumo do conteúdo da página sem o que muda sem mudar o texto: a data (a página é gerada com uma data fixa) e as versões (?v=) dos arquivos."""
    return _resumo(re.sub(r"\?v=[0-9a-f]+", "?v=X", html).encode("utf-8"))


def _datas_das_paginas(feitas, hoje, manifesto):
    """feitas: {chave: função(data) -> html}. Devolve ({chave: data}, manifesto novo).

    A data de uma página só vai para hoje quando o conteúdo dela mudou desde a última geração; se não mudou, fica a data guardada.
    Assim o "Atualizado em", o lastmod do sitemap e o dateModified não mentem quando o robô semanal só regera o site."""
    datas, novo = {}, {}
    for chave, fazer in feitas.items():
        h = _impressao(fazer(DATA_SENTINELA))
        antigo = manifesto.get(chave) or {}
        data = hoje
        if antigo.get("hash") == h:
            try:
                data = datetime.date.fromisoformat(antigo.get("data", ""))
            except ValueError:
                data = hoje
        datas[chave] = data
        novo[chave] = {"hash": h, "data": data.isoformat()}
    return datas, novo


def gerar_site(saida=SAIDA_PADRAO, hoje=None, manifesto=None):
    """manifesto: arquivo com as datas das páginas. Sem ele (e fora da pasta padrão, como nos testes) todas as páginas levam a data de hoje."""
    hoje = hoje or datetime.date.today()
    if manifesto is None and os.path.abspath(saida) == os.path.abspath(SAIDA_PADRAO):
        manifesto = MANIFESTO_PADRAO
    atualizado = hoje.strftime("%d/%m/%Y")
    os.makedirs(saida, exist_ok=True)
    valores = {
        "DOMINIO": DOMINIO, "HUB": HUB, "UMAMI_ID": UMAMI_ID, "RAZAO": RAZAO_SOCIAL, "CNPJ": CNPJ, "EMAIL": EMAIL,
        "ATUALIZADO": atualizado, "CSSV": versao_css(), "ICONV": versao_icones(), "OGV": versao_og_image(), "NAV": _nav_desktop(), "NAVMOBILE": _nav_celular(),
        "FOOT_ENTENDA": _lista_rodape(ENTENDA), "FOOT_LEGAL": _lista_rodape(LEGAL), "FOOT_OUTROS": _lista_outros(),
        "FOOT_TRANSP": _lista_rodape(TRANSPARENCIA, '<li><a class="inline-flex min-h-11 items-center hover:text-white md:min-h-8" href="/feed.xml">Feed Atom</a></li>'),
    }

    def escrever(nome, texto):
        with open(os.path.join(saida, nome), "w", encoding="utf-8", newline="\n") as f:
            f.write(texto)

    def com_data(d):
        return dict(valores, ATUALIZADO=d.strftime("%d/%m/%Y"))

    feitas = {"index": lambda d: _pagina_home(com_data(d), d)}
    for pg in conteudo.PAGINAS:
        feitas[pg["slug"]] = (lambda pg_: lambda d: _pagina_guia(pg_, com_data(d), d, _ctx(d)))(pg)
    datas, novo_manifesto = _datas_das_paginas(feitas, hoje, _ler_manifesto(manifesto))
    escrever("index.html", feitas["index"](datas["index"]))
    for pg in conteudo.PAGINAS:
        escrever(pg["slug"] + ".html", feitas[pg["slug"]](datas[pg["slug"]]))
    if manifesto:
        _gravar_manifesto(manifesto, novo_manifesto)
    valores["ATUALIZADO"] = max(datas.values()).strftime("%d/%m/%Y")  # llms.txt: a data da página mais recente
    escrever("404.html", NOT_FOUND.replace("/styles.css", "/styles.css?v=" + valores["CSSV"]))
    escrever(indexnow.CHAVE + ".txt", indexnow.CHAVE + "\n")
    escrever("feed.xml", feed_atom.gerar(hoje))
    dados_abertos.gerar(os.path.join(saida, "dados"))
    escrever("calculo.js", gerar_calculo_js())
    shutil.copyfile(os.path.join(AQUI, "src", "simulador.js"), os.path.join(saida, "simulador.js"))
    shutil.copyfile(os.path.join(AQUI, "src", "menu.js"), os.path.join(saida, "menu.js"))
    os.makedirs(os.path.join(saida, ".well-known"), exist_ok=True)
    escrever(".well-known/security.txt", "Contact: mailto:" + EMAIL + "\nExpires: " + (hoje + datetime.timedelta(days=365)).isoformat() +
             "T00:00:00.000Z\nPreferred-Languages: pt, en\nCanonical: " + DOMINIO + "/.well-known/security.txt\n")
    escrever("_headers", _preencher(HEADERS, {"CSP": CSP}))
    escrever("robots.txt", "User-agent: *\nAllow: /\n\nSitemap: " + DOMINIO + "/sitemap.xml\n")
    linhas = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for caminho in PAGINAS_INDEXAVEIS:
        linhas.append("  <url><loc>" + DOMINIO + caminho + "</loc><lastmod>" + datas["index" if caminho == "/" else caminho[1:]].isoformat() + "</lastmod></url>")
    linhas.append("</urlset>")
    escrever("sitemap.xml", "\n".join(linhas) + "\n")
    lista = "\n".join("- " + DOMINIO + c for c in PAGINAS_INDEXAVEIS)
    escrever("llms.txt", _preencher(LLMS, dict(valores, LISTA=lista)))
    return saida


if __name__ == "__main__":
    pasta = sys.argv[1] if len(sys.argv) > 1 else SAIDA_PADRAO
    print("Site gerado em", gerar_site(pasta))
