"""Gera o site estático do simulador de empréstimo via cartão de crédito ("Pix no cartão").

Saída em paginas_seo/ (publicada no Cloudflare Pages). O CSS vem do Tailwind (npm run build:css).
Uso: python gerador_emprestimo.py [pasta_de_saida]

Regras do projeto: poucas páginas, cada uma com conteúdo próprio (nada de grade de páginas quase iguais);
nenhum dado pessoal; medição só com Umami (sem cookies).
"""
import datetime
import json
import os
import shutil
import sys

import calculo

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA_PADRAO = os.path.join(AQUI, "paginas_seo")

DOMINIO = "https://emprestimo.datalabglobal.com"
HUB = "https://www.datalabglobal.com"
UMAMI_ID = "ba3c0b88-59e8-47dd-866d-0b05e5e7dae9"
RAZAO_SOCIAL = "Satori Soluções Comerciais LTDA"
CNPJ = "63.998.502/0001-73"
EMAIL = "contato@datalabglobal.com"

# Páginas indexáveis (entram no sitemap). Fase 3 acrescenta os guias, cada um com conteúdo próprio.
PAGINAS_INDEXAVEIS = ["/"]

CSP = (
    "default-src 'self'; "
    "script-src 'self' https://static.cloudflareinsights.com https://cloud.umami.is; "
    "style-src 'self'; "
    "img-src 'self' data:; "
    "font-src 'self'; "
    "connect-src 'self' https://api.triagem.digital https://cloudflareinsights.com https://cloud.umami.is https://gateway.umami.is; "
    "frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
)

HEADERS = """/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Strict-Transport-Security: max-age=31536000; includeSubDomains
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: geolocation=(), camera=(), microphone=(), payment=()
  Content-Security-Policy: @@CSP@@

/styles.css
  Cache-Control: public, max-age=31536000, immutable

/calculo.js
  Cache-Control: public, max-age=3600, must-revalidate

/simulador.js
  Cache-Control: public, max-age=3600, must-revalidate

/logo-header.webp
  Cache-Control: public, max-age=86400, must-revalidate

/og-image.png
  Cache-Control: public, max-age=86400, must-revalidate
"""

CALCULO_JS = """/* GERADO por gerador_emprestimo.py a partir de dados/pix-tabela-esperada.json. Não edite à mão.
   Mesma conta de calculo.py (os testes comparam os dois). */
(function (root) {
  'use strict';
  var T = @@TABELA@@;
  var PIX_MIN = @@PIX_MIN@@;
  var PIX_MAX = T.pix_max;

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

  var api = { simular: simular, brl: brl, pct: pct, PIX_MIN: PIX_MIN, PIX_MAX: PIX_MAX, tableUUID: T.table_uuid, tabela: T };
  root.DatalabPix = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);
"""

HOME = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pix no cartão de crédito: simule parcela, IOF e CET</title>
<meta name="description" content="Simule o Pix no cartão de crédito (R$ 300 a R$ 5.000, em 2x a 12x) e veja parcela, total na fatura, IOF e CET antes de contratar. Crédito caro: confira o custo.">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="@@DOMINIO@@/">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/favicon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="Datalab Global">
<meta property="og:title" content="Pix no cartão de crédito: simule parcela, IOF e CET">
<meta property="og:description" content="Veja o custo real antes de contratar: parcela, total na fatura, IOF e CET.">
<meta property="og:url" content="@@DOMINIO@@/">
<meta property="og:image" content="@@DOMINIO@@/og-image.png">
<meta name="theme-color" content="#0A192F">
<link rel="stylesheet" href="/styles.css">
<script defer src="https://cloud.umami.is/script.js" data-website-id="@@UMAMI_ID@@"></script>
</head>
<body>
<header class="mx-auto flex max-w-5xl items-center justify-between px-4 py-5">
  <a href="@@HUB@@/" class="flex items-center gap-2" aria-label="Datalab Global">
    <img src="/logo-header.webp" alt="Datalab Global" width="168" height="40" class="h-9 w-auto">
  </a>
  <a href="@@HUB@@/" class="text-sm text-slate-400 hover:text-white">Outros simuladores</a>
</header>

<main class="mx-auto max-w-5xl px-4 pb-16">
  <section class="pt-4 pb-8">
    <h1 class="text-3xl font-extrabold leading-tight sm:text-4xl">Pix no cartão de crédito: veja o custo real antes de contratar</h1>
    <p class="mt-3 max-w-3xl text-slate-300">Você recebe um Pix na conta e paga em parcelas na fatura do cartão. É crédito caro: aqui o custo aparece primeiro, antes de qualquer botão.</p>
  </section>

  <section id="simulador" aria-labelledby="titulo-simulador" class="painel rounded-3xl p-5 sm:p-8">
    <h2 id="titulo-simulador" class="text-xs font-bold uppercase tracking-widest text-slate-400">Simulação</h2>
    <div class="mt-5 grid gap-6 lg:grid-cols-2">
      <div class="flex flex-col gap-4">
        <div role="tablist" class="grid grid-cols-2 gap-1 rounded-2xl border border-white/10 bg-slate-950/60 p-1.5">
          <button id="btn-modo-valor" type="button" role="tab" aria-selected="true" class="rounded-xl px-2 py-3 text-sm font-bold text-slate-300 aria-selected:bg-violet-700 aria-selected:text-white">Quero um valor<span class="block text-xs font-normal opacity-80">quanto cai na conta</span></button>
          <button id="btn-modo-limite" type="button" role="tab" aria-selected="false" class="rounded-xl px-2 py-3 text-sm font-bold text-slate-300 aria-selected:bg-violet-700 aria-selected:text-white">Usar meu limite<span class="block text-xs font-normal opacity-80">quanto tenho no cartão</span></button>
        </div>

        <div class="rounded-2xl border border-white/10 bg-slate-900/40 p-5">
          <div class="flex items-center justify-between gap-3">
            <label id="rotulo-valor" for="campo-valor" class="text-xs font-bold uppercase tracking-widest text-slate-400">Valor que você quer no Pix</label>
            <div class="flex items-baseline gap-1"><span class="font-bold text-white">R$</span>
              <input id="campo-valor" type="number" inputmode="numeric" min="300" max="5000" step="50" value="1000" class="num w-28 bg-transparent text-right text-2xl font-bold text-white">
            </div>
          </div>
          <input id="range-valor" aria-labelledby="rotulo-valor" type="range" min="300" max="5000" step="50" value="1000" class="mt-4">
          <div class="mt-2 flex justify-between text-xs text-slate-400"><span id="min-valor">R$ 300,00</span><span id="max-valor">R$ 5.000,00</span></div>
        </div>

        <div class="rounded-2xl border border-white/10 bg-slate-900/40 p-5">
          <div class="flex items-center justify-between">
            <label for="range-parcelas" class="text-xs font-bold uppercase tracking-widest text-slate-400">Parcelas na fatura</label>
            <span id="txt-parcelas" class="num text-2xl font-extrabold text-white">12x</span>
          </div>
          <input id="range-parcelas" type="range" min="2" max="12" step="1" value="12" class="mt-4">
          <div class="mt-2 flex justify-between text-xs text-slate-400"><span>2x</span><span>12x</span></div>
        </div>
      </div>

      <div aria-live="polite" class="flex flex-col gap-5 rounded-2xl border border-white/10 bg-slate-950/80 p-6">
        <div>
          <div class="text-xs font-bold uppercase tracking-widest text-slate-400">Você recebe via Pix</div>
          <div id="r-pix" class="num mt-1 text-4xl font-extrabold text-violet-400">R$ 1.000,00</div>
        </div>
        <div>
          <div class="text-xs font-bold uppercase tracking-widest text-slate-400">E paga na fatura do cartão</div>
          <div id="r-parcelas" class="num mt-1 text-2xl font-extrabold text-white">12 parcelas</div>
        </div>
        <div class="rounded-xl border border-amber-400/40 bg-amber-400/10 p-4 text-sm text-amber-100">
          <p id="r-custo-texto" class="font-semibold"></p>
          <p class="mt-1 text-amber-200/90">Custo efetivo total (CET): <strong id="r-cet" class="num"></strong>. Juros: <strong id="r-juros" class="num"></strong>.</p>
        </div>
        <dl class="grid grid-cols-2 gap-4 border-t border-white/10 pt-4 text-sm">
          <div><dt class="text-xs font-bold uppercase tracking-widest text-slate-400">Total na fatura</dt><dd id="r-total" class="num mt-1 text-lg font-bold text-white"></dd></div>
          <div><dt class="text-xs font-bold uppercase tracking-widest text-slate-400">IOF (já incluso)</dt><dd id="r-iof" class="num mt-1 text-lg font-bold text-white"></dd></div>
        </dl>
        <p id="aviso-minimo" class="hidden text-sm text-amber-300">Com esse limite, o Pix ficaria abaixo do mínimo de R$ 300. Aumente o limite ou diminua as parcelas.</p>
        <button id="cta-pix" type="button" class="mt-auto w-full rounded-xl bg-violet-400 px-4 py-4 text-base font-extrabold text-slate-950">Ver minha proposta</button>
        <p id="aviso-celular" class="hidden text-center text-xs text-slate-400">A contratação é feita pelo celular: na próxima tela do parceiro, aponte a câmera para o QR Code e a proposta abre já preenchida. Tenha em mãos o RG ou a CNH original.</p>
        <p class="text-center text-xs text-slate-400">Você não digita dado pessoal aqui. A contratação acontece no ambiente do parceiro e depende de análise de crédito.</p>
      </div>
    </div>

    <div class="mt-6 rounded-2xl border border-violet-400/25 bg-violet-400/10 p-5">
      <h3 class="text-xs font-bold uppercase tracking-widest text-white">Compare os prazos para o mesmo valor</h3>
      <div id="comparativo" class="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4"></div>
      <p id="txt-comparativo" class="mt-3 text-sm text-slate-300"></p>
    </div>
  </section>

  <section class="mt-10 grid gap-6 sm:grid-cols-2">
    <div class="painel rounded-2xl p-6">
      <h2 class="text-lg font-bold">Quanto custa, de verdade</h2>
      <p class="mt-2 text-sm text-slate-300">O CET vai de 34,64% ao mês (2x) a 7,49% ao mês (12x). Ao ano, de 3.621% a 148,97%. Por isso o simulador mostra quanto você paga a mais antes do botão. Se você consegue outra forma de crédito mais barata, ela costuma valer mais a pena.</p>
    </div>
    <div class="painel rounded-2xl p-6">
      <h2 class="text-lg font-bold">Quem oferece</h2>
      <p class="mt-2 text-sm text-slate-300">A oferta é de um correspondente bancário parceiro. O contrato é uma Cédula de Crédito Bancário (CCB), e a aprovação depende de análise de crédito: não há garantia de aprovação nem de valor.</p>
    </div>
  </section>
</main>

<footer class="border-t border-white/10 bg-slate-950/60">
  <div class="mx-auto max-w-5xl px-4 py-8 text-sm text-slate-400">
    <p>Atualizado em @@ATUALIZADO@@. Condições da Tabela 10 do parceiro, conferidas automaticamente toda semana.</p>
    <p class="mt-2">Datalab Global é marca de @@RAZAO@@, CNPJ @@CNPJ@@. Contato: <a class="underline" href="mailto:@@EMAIL@@">@@EMAIL@@</a>.</p>
    <p class="mt-2"><a class="underline" href="@@HUB@@/privacidade/">Privacidade</a> · <a class="underline" href="@@HUB@@/termos/">Termos de uso</a></p>
    <p class="mt-2 text-xs">A simulação não é proposta de crédito. Crédito sujeito a análise e aprovação.</p>
  </div>
</footer>

<script src="/calculo.js"></script>
<script src="/simulador.js"></script>
</body>
</html>
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
  <p class="mt-6"><a class="underline" href="/">Voltar ao simulador do Pix no cartão</a></p>
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
- A aprovação depende de análise de crédito. A simulação não é proposta de crédito.

## Páginas
@@LISTA@@
"""


def _preencher(texto, valores):
    for chave, valor in valores.items():
        texto = texto.replace("@@" + chave + "@@", valor)
    return texto


def gerar_calculo_js():
    tabela = json.dumps(calculo.TABELA, ensure_ascii=False, sort_keys=True)
    return _preencher(CALCULO_JS, {"TABELA": tabela, "PIX_MIN": str(calculo.PIX_MIN)})


def gerar_site(saida=SAIDA_PADRAO, hoje=None):
    hoje = hoje or datetime.date.today()
    atualizado = hoje.strftime("%d/%m/%Y")
    os.makedirs(saida, exist_ok=True)
    valores = {
        "DOMINIO": DOMINIO, "HUB": HUB, "UMAMI_ID": UMAMI_ID, "RAZAO": RAZAO_SOCIAL,
        "CNPJ": CNPJ, "EMAIL": EMAIL, "ATUALIZADO": atualizado,
    }

    def escrever(nome, conteudo):
        with open(os.path.join(saida, nome), "w", encoding="utf-8", newline="\n") as f:
            f.write(conteudo)

    escrever("index.html", _preencher(HOME, valores))
    escrever("404.html", NOT_FOUND)
    escrever("calculo.js", gerar_calculo_js())
    shutil.copyfile(os.path.join(AQUI, "src", "simulador.js"), os.path.join(saida, "simulador.js"))
    escrever("_headers", _preencher(HEADERS, {"CSP": CSP}))
    escrever("robots.txt", "User-agent: *\nAllow: /\n\nSitemap: " + DOMINIO + "/sitemap.xml\n")
    linhas = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for caminho in PAGINAS_INDEXAVEIS:
        linhas.append("  <url><loc>" + DOMINIO + caminho + "</loc><lastmod>" + hoje.isoformat() + "</lastmod></url>")
    linhas.append("</urlset>")
    escrever("sitemap.xml", "\n".join(linhas) + "\n")
    lista = "\n".join("- " + DOMINIO + c for c in PAGINAS_INDEXAVEIS)
    escrever("llms.txt", _preencher(LLMS, dict(valores, LISTA=lista)))
    return saida


if __name__ == "__main__":
    pasta = sys.argv[1] if len(sys.argv) > 1 else SAIDA_PADRAO
    print("Site gerado em", gerar_site(pasta))
