"""Gera o site estático do simulador do Empréstimo pessoal com crédito do cartão (o limite do cartão é a fonte do dinheiro, entregue por Pix).

Saída em paginas_seo/ (publicada no Cloudflare Pages, sem build). O CSS é escrito à mão em src/estilo.css e copiado para paginas_seo/styles.css.
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
# Ambiente de contratação do parceiro (sem o código da simulação). Só no link de reserva da tela de confirmação; o botão principal pede antes a simulação ao parceiro.
CHECKOUT = "https://checkoutonline.digital/?l=" + calculo.TABELA["table_uuid"] + "&u=ucHWD4k1tat4&lp=gyroo&wl=gyroo&s="

# Data de atualização de cada página: só muda quando o conteúdo muda (ver _datas_das_paginas). O arquivo fica no repositório
# e o robô semanal o commita junto com as páginas.
MANIFESTO_PADRAO = os.path.join(AQUI, "dados", "datas_paginas.json")
DATA_SENTINELA = datetime.date(2000, 1, 1)

HOME_TITLE = "Empréstimo pessoal com crédito do cartão: parcela e IOF"
HOME_DESC = ("Simule o empréstimo pessoal com crédito do cartão: receba R$ 300 a R$ 5.000 por Pix e pague em 2x a 12x na fatura. "
             "Veja parcela, IOF e CET.")

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
  Cache-Control: public, max-age=31536000, immutable

/simulador.js
  Cache-Control: public, max-age=31536000, immutable

/menu.js
  Cache-Control: public, max-age=31536000, immutable

/og-image.png
  Cache-Control: public, max-age=86400, must-revalidate

/favicon.ico
  Cache-Control: public, max-age=86400, must-revalidate

/fonts/*
  Cache-Control: public, max-age=31536000, immutable
"""

CALCULO_JS = """/* GERADO por gerador_emprestimo.py a partir de dados/emprestimo-cartao-tabela-esperada.json. Não edite à mão.
   Mesma conta de calculo.py (os testes comparam os dois). */
(function (root) {
  'use strict';
  var T = @@TABELA@@;
  var VALOR_MIN = @@VALOR_MIN@@;
  var VALOR_MAX = T.valor_max;
  // Taxas médias de juros do Banco Central (referência, não oferta): aa = ao ano, am = ao mês equivalente (juros compostos).
  var REF = @@REFERENCIAS@@;

  function simular(modo, valor, limite, parcelas) {
    var fator = T.fator_base + T.fator_por_parcela * parcelas;
    var receber = modo === 'valor' ? valor : Math.min(limite / (1 + fator), VALOR_MAX);
    var total = receber * (1 + fator);
    var cet = T.cet[String(parcelas)];
    return {
      receber: receber,
      total: total,
      parcela: total / parcelas,
      iof: receber * (T.iof_fixo + T.iof_por_parcela * parcelas),
      jurosMes: cet.monthly,
      cetAno: cet.annual
    };
  }

  // Juros ao mês (em %) de um empréstimo em que você recebe "receber" e paga n parcelas iguais de "parcela". Mesma conta de calculo.taxa_implicita.
  function taxaImplicita(receber, parcela, n) {
    if (receber <= 0 || parcela * n <= receber) return null;
    var lo = 0, hi = 5;
    for (var k = 0; k < 200; k++) {
      var i = (lo + hi) / 2;
      var vp = i > 0 ? parcela * (1 - Math.pow(1 + i, -n)) / i : parcela * n;
      if (vp > receber) lo = i; else hi = i;
    }
    return (lo + hi) / 2 * 100;
  }

  function brl(v) { return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v); }
  function pct(v) { return v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + '%'; }

  var api = { simular: simular, taxaImplicita: taxaImplicita, brl: brl, pct: pct, VALOR_MIN: VALOR_MIN, VALOR_MAX: VALOR_MAX, tableUUID: T.table_uuid, tabela: T, referencias: REF };
  root.DatalabEmprestimo = api;
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
<main class="wrap">
<section class="hero">
  <h1>Página não encontrada</h1>
  <p>O endereço não existe mais ou foi digitado errado.</p>
  <p class="fine"><a class="btn" href="/">Voltar ao simulador do empréstimo com crédito do cartão</a></p>
</section>
</main>
</body>
</html>
"""

LLMS = """# Empréstimo pessoal com crédito do cartão (Datalab Global)

> Simulador gratuito do empréstimo pessoal com crédito do cartão: o limite do cartão de crédito é a fonte do dinheiro, que você recebe por Pix (de R$ 300 a R$ 5.000) e paga em 2x a 12x na fatura. Mostra parcela, total na fatura, IOF e CET antes de qualquer contratação. É crédito caro.

- Responsável: @@RAZAO@@, CNPJ @@CNPJ@@
- Atualizado em @@ATUALIZADO@@
- Fonte dos números: Tabela 10 do parceiro (correspondente bancário), conferida toda semana pela API do próprio parceiro.
- Conta: fator = 0,5479 + 0,003 x parcelas; parcela = valor x (1 + fator) / parcelas; IOF = valor x (0,0038 + 0,00246 x parcelas).
- A aprovação depende de análise de crédito. A simulação não é proposta de crédito.
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
    """Última taxa média do BCB de cada série, para o simulador comparar com os juros do empréstimo. Sem dado, lista vazia (o bloco some)."""
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
    return _preencher(CALCULO_JS, {"TABELA": tabela, "VALOR_MIN": str(calculo.VALOR_MIN), "REFERENCIAS": refs})


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
    """Resumo do src/estilo.css (copiado para styles.css). O arquivo tem cache de 1 ano e imutável; a versão no endereço (?v=) faz o navegador buscar o novo quando o CSS muda."""
    with open(os.path.join(AQUI, "src", "estilo.css"), "rb") as f:
        return _resumo(f.read())


def versao_icones():
    """Resumo dos ícones. Sem a versão na URL, quem já visitou continuaria vendo o ícone antigo pelo cache."""
    h = hashlib.sha256()
    for nome in ("favicon.ico", "favicon-32.png", "apple-touch-icon.png"):
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
DESTAQUES = ["como-funciona", "custo-cet-iof", "taxas-de-referencia"]
ENTENDA = ["como-funciona", "e-seguro-golpes", "custo-cet-iof", conteudo.SLUG_COMPARAR, "quando-nao-vale-a-pena"]
TRANSPARENCIA = ["taxas-de-referencia", "metodologia", "dados-abertos", "atualizacoes", "sobre"]
LEGAL = ["privacidade", "termos"]
ROTULOS = {"atualizacoes": "Atualizações", "dados-abertos": "Dados abertos", "privacidade": "Privacidade", "termos": "Termos de uso",
           conteudo.SLUG_COMPARAR: "Comparar com outros créditos", "taxas-de-referencia": "Taxas do Banco Central",
           "custo-cet-iof": "CET e IOF", "e-seguro-golpes": "É seguro? Golpes", "quando-nao-vale-a-pena": "Quando não vale a pena"}


def _pg(slug):
    return next(pg for pg in conteudo.PAGINAS if pg["slug"] == slug)


def _rotulo(slug):
    return ROTULOS.get(slug) or _pg(slug).get("menu") or _pg(slug)["h1"]


def _nav_desktop():
    return '<a href="/#simulador">Simular</a>' + "".join('<a href="/' + x + '">' + _rotulo(x) + "</a>" for x in DESTAQUES)


def _nav_celular():
    links = ENTENDA + [x for x in TRANSPARENCIA if x not in ENTENDA]
    return '<a href="/#simulador">Simular</a>' + "".join('<a href="/' + x + '">' + _rotulo(x) + "</a>" for x in links)


def _lista_rodape(slugs, extra=""):
    return "".join('<li><a href="/' + x + '">' + _rotulo(x) + "</a></li>" for x in slugs) + extra


# Os outros simuladores da Datalab Global (outros produtos, outros subdomínios). O texto do link descreve o destino.
OUTROS_SIMULADORES = [
    ("https://simulador.datalabglobal.com/", "Financiamento imobiliário"),
    ("https://veiculos.datalabglobal.com/", "Financiamento de veículos"),
    ("https://homeequity.datalabglobal.com/", "Crédito com imóvel em garantia (Home Equity)"),
    ("https://autoequity.datalabglobal.com/", "Crédito com veículo em garantia (Auto Equity)"),
    ("https://condominio.datalabglobal.com/", "Empréstimo para Condomínios"),
    (HUB + "/", "Datalab Global"),
]


def _lista_outros():
    return "".join('<li><a href="' + url + '">' + texto + "</a></li>" for url, texto in OUTROS_SIMULADORES)


def _faq_html():
    return "".join("<details><summary>" + q + "</summary><p>" + r + "</p></details>" for q, r in conteudo.FAQ)


def _cartoes_html():
    saida = ""
    for pg in conteudo.PAGINAS:
        if not pg.get("menu"):
            continue
        saida += '<a class="card" href="/' + pg["slug"] + '"><h4>' + pg["menu"] + "</h4>" + pg["desc"] + '<span class="go">Ler →</span></a>'
    return saida


def _ctx(hoje):
    return {
        "razao": RAZAO_SOCIAL, "cnpj": CNPJ, "email": EMAIL, "atualizado": hoje.strftime("%d/%m/%Y"),
        "atualizacoes": conteudo.ATUALIZACOES,
    }


def _organizacao():
    return {"@type": "Organization", "@id": DOMINIO + "/#organizacao", "name": "Datalab Global", "legalName": RAZAO_SOCIAL,
            "taxID": CNPJ, "url": HUB + "/", "email": EMAIL, "sameAs": ["https://huggingface.co/datalabglobal"], "founder": {"@type": "Person", "name": "Rodolfo Delfino", "sameAs": ["https://github.com/rldelfino", "https://www.kaggle.com/rodolfodelfino", "https://www.linkedin.com/in/rodolfo-leal-delfino"]}, "logo": {"@type": "ImageObject", "url": DOMINIO + "/apple-touch-icon.png", "width": 180, "height": 180}}


def _breadcrumb(pg, canonical):
    """Trilha Início > página, para as páginas internas."""
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": conteudo.NOME, "item": DOMINIO + "/"},
        {"@type": "ListItem", "position": 2, "name": pg["h1"], "item": canonical}]}


def _datasets(hoje):
    """Um Dataset (schema.org) para cada conjunto de dados abertos da página /dados-abertos."""
    saida = []
    for c in dados_abertos.CONJUNTOS:
        d = {"@context": "https://schema.org", "@type": "Dataset", "name": c["titulo"], "description": c["descricao"],
             "url": DOMINIO + "/dados-abertos", "inLanguage": "pt-BR", "isAccessibleForFree": True, "license": c["licenca"]["url"],
             "creator": {"@type": "Organization", "name": "Datalab Global", "url": HUB + "/"}, "publisher": {"@id": DOMINIO + "/#organizacao"},
             "dateModified": hoje.isoformat(), "keywords": ["crédito", "juros", "Brasil", "empréstimo com crédito do cartão" if c is dados_abertos.EMPRESTIMO else "Banco Central"],
             "sameAs": [c["kaggle"], c["huggingface"]], "isBasedOn": c["fonte"]["path"],
             "variableMeasured": [{"@type": "PropertyValue", "name": n, "description": desc} for n, _t, desc in c["colunas"]],
             "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": DOMINIO + "/dados/" + c["nome"] + ".csv"},
                              {"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": DOMINIO + "/dados/" + c["nome"] + ".json"}]}
        if c is dados_abertos.BCB:
            meses = sorted({l["mes_referencia"] for l in dados_abertos.linhas_bcb()})
            d["temporalCoverage"] = meses[0] + "/" + meses[-1]
        saida.append(d)
    return saida


def _valores_padrao():
    """Números da simulação inicial (a mesma que o JS desenha ao abrir a página): R$ 1.000 em 12x. Ficam escritos no HTML para quem lê sem JavaScript e para os buscadores."""
    r = calculo.simular("valor", 1000, 0, 12)
    custo = r["total"] - r["receber"]
    return {
        "D_VALOR": "1.000", "D_VALOR_N": "1000",
        "D_PARCELA": conteudo.brl(r["parcela"]), "D_SUB": "12 parcelas · você recebe " + conteudo.brl(r["receber"]), "D_TOTAL": conteudo.brl(r["total"]),
        "D_RECEBER": conteudo.brl(r["receber"]), "D_IOF": conteudo.brl(r["iof"]),
        "D_RESUMO": "Você recebe " + conteudo.brl(r["receber"]) + " e paga " + conteudo.brl(r["total"]) + " na fatura: " + conteudo.brl(custo) + " a mais, com juros e IOF.",
        "D_PCT_CUSTO": str(round(custo / r["total"] * 100)), "D_ROSCA_P": "%.2f" % (r["receber"] / r["total"] * 289.03),
        "D_L_VALOR": conteudo.brl(r["receber"]), "D_L_CUSTO": conteudo.brl(custo),
        "D_NOTA_LIMITE": "O total na fatura (" + conteudo.brl(r["total"]) + ") fica comprometido no limite até as parcelas serem pagas.",
        "D_JUROS": conteudo.pct(r["jurosMes"]), "D_CET": conteudo.pct(r["cetAno"]), "D_REAL": conteudo.brl(r["total"] / r["receber"]),
        "D_DLG_RESUMO": "Você recebe " + conteudo.brl(r["receber"]) + " por Pix e paga " + conteudo.brl(r["total"]) + " na fatura (12x de " + conteudo.brl(r["parcela"]) + "): "
                        + conteudo.brl(custo) + " a mais, com juros e IOF.",
    }


def _pagina_home(valores, hoje):
    faq = {"@context": "https://schema.org", "@type": "FAQPage",
           "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": _sem_tags(r)}} for q, r in conteudo.FAQ]}
    site = {"@context": "https://schema.org", "@graph": [
        _organizacao(),
        {"@type": "WebSite", "@id": DOMINIO + "/#site", "url": DOMINIO + "/", "name": conteudo.NOME + " — Datalab Global", "inLanguage": "pt-BR",
         "publisher": {"@id": DOMINIO + "/#organizacao"}},
        {"@type": "WebApplication", "@id": DOMINIO + "/#app", "url": DOMINIO + "/", "name": "Simulador de " + conteudo.NOME.lower(), "description": HOME_DESC, "inLanguage": "pt-BR",
         "applicationCategory": "FinanceApplication", "operatingSystem": "Any", "browserRequirements": "Requires JavaScript", "isAccessibleForFree": True,
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "BRL"}, "publisher": {"@id": DOMINIO + "/#organizacao"}},
    ]}
    main = _preencher(layout.HOME_MAIN, dict(valores, CARTOES=_cartoes_html(), FAQ=_faq_html(), COMPARA=conteudo.frase_home(), CUSTO_HOME=conteudo.custo_home(),
                                             O_QUE_E=conteudo.O_QUE_E, SLUG_COMPARAR=conteudo.SLUG_COMPARAR, CHECKOUT=CHECKOUT, **_valores_padrao()))
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
    ld = (_ld(artigo) if guia else "") + _ld(_breadcrumb(pg, canonical))
    if pg["slug"] == "dados-abertos":
        ld += "".join(_ld(d) for d in _datasets(hoje))
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


def redirecionamentos():
    """_redirects do Cloudflare Pages: os endereços antigos (nome errado do produto) levam aos novos, com 301.
    Páginas: conteudo.REDIRECIONAMENTOS_SLUG. Arquivos de dados abertos: nome antigo -> nome novo (Kaggle, Hugging Face e dados.gov.br podem ter o link antigo)."""
    linhas = ["# 301: endereços antigos (o produto se chamava \"Pix no cartão\") para os novos. Gerado por gerador_emprestimo.py."]
    for antigo, novo in conteudo.REDIRECIONAMENTOS_SLUG.items():
        linhas.append(antigo + " " + novo + " 301")
        linhas.append(antigo + ".html " + novo + " 301")
    for ext in (".csv", ".json"):
        linhas.append("/dados/pix-no-cartao-tabela-10" + ext + " /dados/" + dados_abertos.EMPRESTIMO["nome"] + ext + " 301")
    linhas.append("/dados/datapackage-pix-no-cartao-tabela-10.json /dados/datapackage-" + dados_abertos.EMPRESTIMO["nome"] + ".json 301")
    return "\n".join(linhas) + "\n"


def gerar_site(saida=SAIDA_PADRAO, hoje=None, manifesto=None):
    """manifesto: arquivo com as datas das páginas. Sem ele (e fora da pasta padrão, como nos testes) todas as páginas levam a data de hoje."""
    hoje = hoje or datetime.date.today()
    if manifesto is None and os.path.abspath(saida) == os.path.abspath(SAIDA_PADRAO):
        manifesto = MANIFESTO_PADRAO
    atualizado = hoje.strftime("%d/%m/%Y")
    os.makedirs(saida, exist_ok=True)
    if os.path.abspath(saida) != os.path.abspath(SAIDA_PADRAO):  # fora da pasta padrão (testes): leva fontes e ícones, que não são gerados
        os.makedirs(os.path.join(saida, "fonts"), exist_ok=True)
        for nome in os.listdir(os.path.join(SAIDA_PADRAO, "fonts")):
            shutil.copyfile(os.path.join(SAIDA_PADRAO, "fonts", nome), os.path.join(saida, "fonts", nome))
        for nome in ("favicon.ico", "favicon-32.png", "favicon-192.png", "apple-touch-icon.png", "og-image.png"):
            shutil.copyfile(os.path.join(SAIDA_PADRAO, nome), os.path.join(saida, nome))
    shutil.copyfile(os.path.join(AQUI, "src", "estilo.css"), os.path.join(saida, "styles.css"))
    valores = {
        "DOMINIO": DOMINIO, "HUB": HUB, "UMAMI_ID": UMAMI_ID, "RAZAO": RAZAO_SOCIAL, "CNPJ": CNPJ, "EMAIL": EMAIL, "LOGO": layout.LOGO,
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
    escrever("_redirects", redirecionamentos())
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
