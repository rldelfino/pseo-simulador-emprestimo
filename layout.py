"""HTML do layout (cabeçalho, rodapé), da home e dos blocos dos guias.

Mesma família visual dos outros simuladores da Datalab Global: fundo navy com brilho, títulos em Playfair Display,
texto em Inter, destaque esmeralda, painéis de vidro. Sem atributo style nem script inline (a CSP não permite).
Os marcadores @@NOME@@ são trocados pelo gerador.
"""

LAYOUT = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>@@TITLE@@</title>
<meta name="description" content="@@DESC@@">
<meta name="robots" content="@@ROBOTS@@">
<link rel="canonical" href="@@CANONICAL@@">
<link rel="icon" href="/favicon.ico?v=@@ICONV@@" sizes="any">
<link rel="icon" href="/favicon-32.png?v=@@ICONV@@" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="/apple-touch-icon.png?v=@@ICONV@@">
<meta property="og:type" content="@@OGTYPE@@">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="Datalab Global">
<meta property="og:title" content="@@TITLE@@">
<meta property="og:description" content="@@DESC@@">
<meta property="og:url" content="@@CANONICAL@@">
<meta property="og:image" content="@@DOMINIO@@/og-image.png?v=@@OGV@@">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="@@TITLE@@">
<meta name="twitter:description" content="@@DESC@@">
<meta name="twitter:image" content="@@DOMINIO@@/og-image.png?v=@@OGV@@">
<meta name="theme-color" content="#020617">
<link rel="preload" href="/fonts/playfair-display-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/styles.css?v=@@CSSV@@">
<link rel="alternate" type="application/atom+xml" title="Pix no cartão — Datalab Global" href="/feed.xml">
@@JSONLD@@<script defer src="https://cloud.umami.is/script.js" data-website-id="@@UMAMI_ID@@"></script>
</head>
<body>
<a href="#conteudo" class="sr-only focus:not-sr-only focus:absolute focus:left-2 focus:top-2 focus:z-[60] focus:rounded focus:bg-white focus:px-3 focus:py-2 focus:text-slate-900">Ir para o conteúdo</a>
<header class="sticky top-0 z-50 border-b border-white/5 bg-slate-950/80 backdrop-blur-md">
  <div class="mx-auto flex max-w-6xl items-center justify-between gap-2 px-4 py-2 sm:gap-4">
    <a href="/" class="flex min-h-11 shrink-0 items-center" aria-label="Pix no cartão — Datalab Global, página inicial">
      <img src="/logo-full.png?v=@@ICONV@@" alt="Datalab Global" width="139" height="48" class="h-9 w-auto drop-shadow-[0_0_15px_rgba(167,139,250,0.25)] sm:h-12">
    </a>
    <nav aria-label="Principal" class="hidden items-center gap-6 text-sm text-slate-300 lg:flex">@@NAV@@</nav>
    <div class="flex items-center gap-2 sm:gap-3">
      <a href="/#simulador" class="inline-flex min-h-11 items-center rounded-full bg-violet-400 px-4 text-xs font-bold text-slate-950 shadow-lg shadow-violet-500/25 hover:bg-violet-300 sm:px-5 sm:text-sm">Simular<span class="hidden sm:inline"> agora</span> &rarr;</a>
      <details class="relative lg:hidden">
        <summary class="inline-flex min-h-11 items-center rounded-lg border border-white/10 px-4 text-xs text-slate-200 sm:text-sm">Menu</summary>
        <nav aria-label="Menu" class="absolute right-0 mt-2 flex w-64 flex-col gap-1 rounded-2xl border border-white/10 bg-slate-900 p-3 text-sm text-slate-200 shadow-2xl">@@NAVMOBILE@@</nav>
      </details>
    </div>
  </div>
</header>

<main id="conteudo" class="mx-auto max-w-6xl px-4 pb-8">
@@MAIN@@
</main>

<footer class="mt-16 border-t border-white/5 bg-slate-950/60">
  <div class="mx-auto grid max-w-6xl gap-10 px-4 py-12 md:grid-cols-5">
    <div>
      <img src="/logo-full.png?v=@@ICONV@@" alt="Datalab Global" width="139" height="48" class="h-12 w-auto" loading="lazy">
      <p class="mt-4 text-sm leading-relaxed text-slate-400">Simulador do Pix no cartão de crédito. O custo aparece antes de qualquer botão.</p>
      <p class="mt-3 text-xs leading-relaxed text-slate-400">A Datalab Global pode receber comissão do parceiro pelas contratações feitas a partir deste site. Não somos banco e não concedemos crédito.</p>
    </div>
    <nav aria-label="Entenda">
      <p class="text-xs font-bold uppercase tracking-widest text-violet-400">Entenda</p>
      <ul class="mt-2 text-sm text-slate-300 md:mt-4">@@FOOT_ENTENDA@@</ul>
    </nav>
    <nav aria-label="Transparência">
      <p class="text-xs font-bold uppercase tracking-widest text-violet-400">Transparência</p>
      <ul class="mt-2 text-sm text-slate-300 md:mt-4">@@FOOT_TRANSP@@</ul>
    </nav>
    <nav aria-label="Legal e mais">
      <p class="text-xs font-bold uppercase tracking-widest text-violet-400">Legal e mais</p>
      <ul class="mt-2 text-sm text-slate-300 md:mt-4">@@FOOT_LEGAL@@</ul>
    </nav>
    <nav aria-label="Outros simuladores da Datalab Global">
      <p class="text-xs font-bold uppercase tracking-widest text-violet-400">Outros simuladores</p>
      <ul class="mt-2 text-sm text-slate-300 md:mt-4">@@FOOT_OUTROS@@</ul>
    </nav>
  </div>
  <div class="border-t border-white/5">
    <div class="mx-auto max-w-6xl px-4 py-6 text-xs leading-relaxed text-slate-400">
      <p>Atualizado em @@ATUALIZADO@@. Condições da Tabela 10 do parceiro, conferidas automaticamente toda semana.</p>
      <p class="mt-1">Datalab Global é marca de @@RAZAO@@, CNPJ @@CNPJ@@. Contato: <a class="underline hover:text-slate-300" href="mailto:@@EMAIL@@">@@EMAIL@@</a>.</p>
      <p class="mt-1">A simulação não é proposta de crédito. Crédito sujeito a análise e aprovação do parceiro, sem garantia de aprovação.</p>
    </div>
  </div>
</footer>
@@SCRIPTS@@</body>
</html>
"""

ROTULO = "text-[11px] font-bold uppercase tracking-widest text-slate-400"

HOME_MAIN = """  <section class="pt-10 text-center sm:pt-14">
    <a href="#simulador" class="mx-auto inline-flex flex-wrap items-center justify-center gap-x-3 gap-y-1 rounded-full border border-white/10 bg-slate-900/60 px-5 py-2 text-xs">
      <span class="font-semibold text-white">Pix no cartão</span>
      <span class="hidden h-3 w-px bg-white/20 sm:block"></span>
      <span class="uppercase tracking-widest text-slate-400">Crédito no cartão</span>
      <span class="hidden h-3 w-px bg-white/20 sm:block"></span>
      <span class="uppercase tracking-widest text-violet-400">Ver o custo &rarr;</span>
    </a>
    <h1 class="mx-auto mt-6 max-w-4xl text-4xl font-bold leading-tight text-white sm:text-5xl lg:text-6xl">Pix no cartão de crédito: veja o custo real antes de contratar</h1>
    <p class="mx-auto mt-5 max-w-2xl text-base leading-relaxed text-slate-300 sm:text-lg">Receba de <strong class="text-white">R$ 300 a R$ 5.000</strong> por Pix e pague em <strong class="text-white">2x a 12x</strong> na fatura do cartão. É crédito caro: o custo aparece primeiro, antes de qualquer botão.</p>
    <p class="mt-5 text-[11px] uppercase tracking-widest text-slate-400">Tabela 10 do parceiro, conferida toda semana. Atualizado em @@ATUALIZADO@@</p>
  </section>

  <section id="simulador" aria-labelledby="titulo-simulador" class="glass-panel mt-10 rounded-[2rem] p-5 sm:p-10">
    <div class="border-b border-white/10 pb-4">
      <h2 id="titulo-simulador" class="text-sm font-bold uppercase tracking-widest text-white sm:text-base">1. Simulação</h2>
      <p class="mt-1 text-xs text-slate-400">Escolha o valor e o prazo. O resultado muda na hora, com todos os custos.</p>
    </div>
    <div class="mt-8 grid gap-6 lg:grid-cols-2">
      <div class="flex flex-col gap-4">
        <div role="tablist" class="grid grid-cols-2 gap-1 rounded-2xl border border-white/10 bg-slate-950/60 p-1.5">
          <button id="btn-modo-valor" type="button" role="tab" aria-selected="true" aria-controls="painel-simulacao" class="rounded-xl px-2 py-3 text-sm font-bold text-slate-400 aria-selected:bg-gradient-to-br aria-selected:from-violet-600 aria-selected:to-violet-800 aria-selected:text-white">Quero um valor<span class="block text-xs font-normal opacity-80">quanto cai na conta</span></button>
          <button id="btn-modo-limite" type="button" role="tab" aria-selected="false" tabindex="-1" aria-controls="painel-simulacao" class="rounded-xl px-2 py-3 text-sm font-bold text-slate-400 aria-selected:bg-gradient-to-br aria-selected:from-violet-600 aria-selected:to-violet-800 aria-selected:text-white">Usar meu limite<span class="block text-xs font-normal opacity-80">quanto tenho no cartão</span></button>
        </div>

        <div id="painel-simulacao" role="tabpanel" aria-labelledby="btn-modo-valor" class="flex flex-col gap-4">

        <div class="tile rounded-2xl p-5">
          <div class="flex items-center justify-between gap-3">
            <label id="rotulo-valor" for="campo-valor" class="@@ROTULO@@">Valor que você quer no Pix</label>
            <div class="flex items-baseline gap-1"><span class="text-lg font-semibold text-slate-300">R$</span>
              <input id="campo-valor" type="text" inputmode="decimal" autocomplete="off" value="1.000" class="num min-h-11 w-32 bg-transparent text-right text-3xl font-semibold text-white">
            </div>
          </div>
          <input id="range-valor" aria-labelledby="rotulo-valor" type="range" min="300" max="5000" step="50" value="1000" class="mt-5">
          <div class="mt-2 flex justify-between text-xs text-slate-400"><span id="min-valor">R$ 300,00</span><span id="max-valor">R$ 5.000,00</span></div>
        </div>

        <div class="tile rounded-2xl p-5">
          <div class="flex items-center justify-between">
            <label for="range-parcelas" class="@@ROTULO@@">Parcelas na fatura</label>
            <span id="txt-parcelas" class="num text-3xl font-semibold text-white">12x</span>
          </div>
          <input id="range-parcelas" type="range" min="2" max="12" step="1" value="12" class="mt-5">
          <div class="mt-2 flex justify-between text-xs text-slate-400"><span>2x</span><span>12x</span></div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="tile rounded-2xl p-5"><p class="@@ROTULO@@">Juros ao mês</p><p id="r-juros" class="num mt-2 text-xl font-semibold text-white"></p></div>
          <div class="tile rounded-2xl p-5"><p class="@@ROTULO@@">CET ao ano</p><p id="r-cet" class="num mt-2 text-xl font-semibold text-white"></p></div>
        </div>
        <div class="tile rounded-2xl p-5">
          <p class="@@ROTULO@@">Composição do total na fatura</p>
          <div class="mt-4 flex flex-wrap items-center gap-6">
            <div id="donut" class="h-[120px] w-[120px] shrink-0" role="img" aria-label="Composição do total na fatura"></div>
            <ul class="space-y-2 text-sm text-slate-300">
              <li class="flex items-center gap-2"><span class="h-2.5 w-2.5 rounded-full bg-violet-500"></span>Valor no seu Pix <strong id="leg-pix" class="num text-white"></strong></li>
              <li class="flex items-center gap-2"><span class="h-2.5 w-2.5 rounded-full bg-amber-500"></span>Juros e IOF <strong id="leg-custo" class="num text-white"></strong></li>
            </ul>
          </div>
        </div>
        </div>
      </div>

      <div id="resultado" aria-live="polite" class="flex flex-col gap-6 rounded-3xl border border-white/10 bg-slate-950/90 p-6 sm:p-8">
        <p class="flex items-center gap-2 text-[11px] font-bold uppercase tracking-widest text-violet-400"><span class="h-2 w-2 rounded-full bg-violet-400 shadow-[0_0_10px_#a78bfa]"></span>Resultado da simulação</p>
        <div>
          <p class="@@ROTULO@@">Você recebe via Pix</p>
          <p id="r-pix" class="num mt-2 text-4xl font-semibold text-white sm:text-5xl">R$ 1.000,00</p>
        </div>
        <div>
          <p class="@@ROTULO@@">E paga na fatura do cartão</p>
          <p id="r-parcelas" class="num mt-2 text-2xl text-slate-200">12 parcelas</p>
        </div>
        <dl class="grid grid-cols-2 gap-4 border-t border-white/10 pt-5">
          <div><dt class="@@ROTULO@@">Total na fatura</dt><dd id="r-total" class="num mt-2 text-xl font-semibold text-violet-300"></dd></div>
          <div><dt class="@@ROTULO@@">IOF (já incluso)</dt><dd id="r-iof" class="num mt-2 text-xl font-semibold text-white"></dd></div>
        </dl>
        <div class="rounded-2xl border border-amber-400/30 bg-amber-400/10 p-4 text-sm text-amber-100">
          <p id="r-custo-texto" class="font-semibold leading-relaxed"></p>
        </div>
        <div id="referencia" aria-live="off" class="hidden rounded-2xl border border-white/10 bg-slate-900/50 p-4">
          <p class="@@ROTULO@@">E o mercado? Juros ao mês</p>
          <ul id="ref-lista" class="mt-3 space-y-2 text-sm"></ul>
          <p id="ref-veredito" class="mt-3 text-sm font-semibold leading-relaxed text-white"></p>
          <p id="ref-nota" class="mt-2 text-xs leading-relaxed text-slate-400"></p>
          <a class="mt-1 inline-flex min-h-11 items-center text-xs font-semibold text-violet-300 underline hover:text-white" href="/taxas-de-referencia">Ver as taxas do Banco Central e a fonte &rarr;</a>
        </div>
        <p id="aviso-minimo" class="hidden text-sm text-amber-300">Com esse limite, o Pix ficaria abaixo do mínimo de R$ 300. Aumente o limite ou diminua as parcelas.</p>
        <div id="aviso-proposta" class="hidden rounded-2xl border border-amber-400/40 bg-amber-400/10 p-4 text-sm text-amber-100">
          <p id="txt-aviso-proposta"></p>
          <a id="link-parceiro" href="#" rel="noopener" class="mt-3 inline-flex min-h-11 items-center font-semibold text-violet-300 underline hover:text-white">Continuar mesmo assim &rarr;</a>
        </div>
        <p id="aviso-pedido" class="text-center text-xs leading-relaxed text-slate-300">No parceiro você faz o pedido real: 6 passos, com CPF e documento original (RG ou CNH). Clique só se quiser contratar.</p>
        <button id="cta-pix" type="button" class="mt-auto w-full rounded-2xl bg-violet-400 px-5 py-4 text-base font-extrabold text-slate-950 shadow-lg shadow-violet-500/25 hover:bg-violet-300">Ver minha proposta &rarr;</button>
        <button id="btn-copiar" type="button" class="inline-flex min-h-11 w-full items-center justify-center rounded-2xl border border-white/15 px-4 text-sm font-semibold text-violet-300 hover:border-violet-400/40 hover:text-white">Copiar o link desta simulação</button>
        <p id="msg-copiado" role="status" class="hidden text-center text-xs text-violet-300"></p>
        <p id="aviso-celular" class="hidden text-center text-xs text-slate-400">A contratação é feita pelo celular: na próxima tela do parceiro, aponte a câmera para o QR Code e a proposta abre já preenchida. Tenha em mãos o RG ou a CNH original.</p>
        <p class="text-center text-xs text-slate-400">Você não digita dado pessoal aqui. A contratação acontece no ambiente do parceiro e depende de análise de crédito.</p>
      </div>
    </div>
  </section>

  <section aria-labelledby="titulo-dica" class="glass-panel-violet mt-8 rounded-[2rem] p-5 sm:p-10">
    <div class="flex flex-wrap items-center gap-3">
      <span class="rounded-md bg-violet-400 px-2 py-0.5 text-xs font-extrabold uppercase tracking-widest text-violet-950">Dica</span>
      <h2 id="titulo-dica" class="text-sm font-bold uppercase tracking-widest text-white sm:text-base">O custo quase não muda com o prazo</h2>
    </div>
    <div class="mt-6 grid gap-8 lg:grid-cols-5">
      <div class="min-w-0 lg:col-span-3">
        <p class="@@ROTULO@@">Quanto você paga a mais, em reais, por prazo</p>
        <div id="barras" class="mt-4 flex flex-col gap-1.5"></div>
      </div>
      <div class="text-sm leading-relaxed text-slate-300 lg:col-span-2 lg:border-l lg:border-white/10 lg:pl-8">
        <p id="txt-barras"></p>
        <p class="mt-4">Prazo maior deixa a prestação menor, mas o dinheiro fica emprestado por mais tempo. O que pesa de verdade é o valor em reais da barra.</p>
        <p class="mt-4"><a class="inline-flex min-h-11 items-center font-semibold text-violet-300 underline hover:text-white" href="/custo-cet-iof">Entenda CET e IOF &rarr;</a></p>
        <p><a class="inline-flex min-h-11 items-center font-semibold text-violet-300 underline hover:text-white" href="/pix-no-cartao-ou-outro-credito">Compare com outros créditos &rarr;</a></p>
      </div>
    </div>
    <details id="detalhe-prazos" class="mt-8 rounded-2xl border border-white/10 bg-slate-950/40 p-4">
      <summary class="flex min-h-11 cursor-pointer items-center font-semibold text-white">Ver a tabela de todos os prazos (2x a 12x)</summary>
      <div class="mt-3 overflow-x-auto">
        <table class="w-full min-w-[34rem] border-collapse text-left text-sm">
          <caption id="cap-prazos" class="pb-2 text-left text-xs text-slate-400"></caption>
          <thead><tr>
            <th scope="col" class="border-b border-white/15 px-3 py-2 text-[11px] font-bold uppercase tracking-widest text-violet-400">Prazo</th>
            <th scope="col" class="border-b border-white/15 px-3 py-2 text-[11px] font-bold uppercase tracking-widest text-violet-400">Parcela</th>
            <th scope="col" class="border-b border-white/15 px-3 py-2 text-[11px] font-bold uppercase tracking-widest text-violet-400">Total na fatura</th>
            <th scope="col" class="border-b border-white/15 px-3 py-2 text-[11px] font-bold uppercase tracking-widest text-violet-400">Custo a mais</th>
            <th scope="col" class="border-b border-white/15 px-3 py-2 text-[11px] font-bold uppercase tracking-widest text-violet-400">Juros ao mês</th>
            <th scope="col" class="border-b border-white/15 px-3 py-2 text-[11px] font-bold uppercase tracking-widest text-violet-400">CET ao ano</th>
          </tr></thead>
          <tbody id="corpo-prazos"></tbody>
        </table>
      </div>
    </details>
  </section>

  <section class="mt-8 grid gap-6 sm:grid-cols-2">
    <div class="glass-panel rounded-3xl p-6 sm:p-8">
      <h2 class="text-xl font-bold text-white">Quanto custa, de verdade</h2>
      <p class="mt-3 text-sm leading-relaxed text-slate-300">Os juros vão de 34,64% ao mês (2x) a 7,49% ao mês (12x). O CET, que inclui o IOF e é contado ao ano, vai de 3.621% a 148,97%. Por isso o simulador mostra quanto você paga a mais antes do botão. Se você consegue outra forma de crédito mais barata, ela costuma valer mais a pena. <a class="font-semibold text-violet-300 underline" href="/custo-cet-iof">Veja a tabela completa</a>.</p>
      <p class="mt-3 text-sm leading-relaxed text-slate-300">@@COMPARA@@</p>
    </div>
    <div class="glass-panel rounded-3xl p-6 sm:p-8">
      <h2 class="text-xl font-bold text-white">Quem oferece</h2>
      <p class="mt-3 text-sm leading-relaxed text-slate-300">A oferta é de um correspondente bancário parceiro. O contrato é uma Cédula de Crédito Bancário (CCB), e a aprovação depende de análise de crédito: não há garantia de aprovação nem de valor. A Datalab Global pode receber comissão do parceiro. <a class="font-semibold text-violet-300 underline" href="/sobre">Saiba mais</a>.</p>
    </div>
  </section>

  <section class="mt-14" aria-labelledby="guias">
    <h2 id="guias" class="text-sm font-bold uppercase tracking-widest text-white sm:text-base">2. Entenda antes de decidir</h2>
    <div class="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">@@CARTOES@@</div>
  </section>

  <section class="mt-14" aria-labelledby="duvidas">
    <h2 id="duvidas" class="text-sm font-bold uppercase tracking-widest text-white sm:text-base">3. Perguntas frequentes</h2>
    <div class="mt-5 flex max-w-3xl flex-col gap-3">@@FAQ@@</div>
  </section>

  <section class="mt-14 rounded-[2rem] bg-gradient-to-br from-violet-600 to-violet-900 p-8 shadow-2xl shadow-violet-950/40 sm:p-12">
    <div class="grid items-center gap-8 md:grid-cols-3">
      <div class="md:col-span-2">
        <span class="inline-block rounded-md bg-amber-400 px-2.5 py-1 text-xs font-extrabold uppercase tracking-widest text-amber-950">Antes de contratar</span>
        <p class="font-serif mt-4 text-3xl font-bold leading-tight text-white sm:text-4xl">Compare o custo e só então peça a proposta.</p>
        <p class="mt-4 text-violet-50/90">A contratação é feita no ambiente de um parceiro (correspondente bancário) e depende de análise de crédito. Sem garantia de aprovação.</p>
      </div>
      <div class="md:text-right">
        <a href="#simulador" class="inline-block rounded-2xl bg-white px-6 py-4 text-sm font-extrabold uppercase tracking-wide text-violet-900 hover:bg-violet-50">Voltar ao simulador</a>
      </div>
    </div>
  </section>

  <div id="barra-resumo" class="hidden fixed inset-x-0 bottom-0 z-30 border-t border-white/10 bg-slate-950/95 px-4 py-2 backdrop-blur lg:hidden">
    <button id="btn-resumo" type="button" class="mx-auto flex min-h-11 w-full max-w-md items-center justify-between gap-3 text-left">
      <span class="min-w-0">
        <span id="resumo-parcela" class="num block truncate text-sm font-semibold text-white"></span>
        <span id="resumo-total" class="num block truncate text-xs text-slate-400"></span>
      </span>
      <span class="shrink-0 rounded-full bg-violet-400 px-4 py-2 text-xs font-bold text-slate-950">Ver resultado &darr;</span>
    </button>
  </div>
"""

GUIA_CABECALHO = """<nav aria-label="Você está em" class="pt-8 text-center">
  <a href="/" class="inline-flex flex-wrap items-center justify-center gap-x-3 gap-y-1 rounded-full border border-white/10 bg-slate-900/60 min-h-11 px-5 py-2 text-xs">
    <span class="font-semibold text-white">Pix no cartão</span>
    <span class="hidden h-3 w-px bg-white/20 sm:block"></span>
    <span class="uppercase tracking-widest text-violet-400">@@ROTULO_PAGINA@@</span>
  </a>
</nav>
<article class="mx-auto max-w-3xl pb-4">
  <h1 class="mt-6 text-center text-3xl font-bold leading-tight text-white sm:text-4xl lg:text-5xl">@@H1@@</h1>
  <p class="mt-4 text-center text-[11px] uppercase tracking-widest text-slate-400">Atualizado em @@ATUALIZADO@@ &middot; @@RAZAO@@</p>
  <div class="glass-panel mt-10 rounded-[2rem] p-6 sm:p-10">
"""

GUIA_MEIO = """  </div>
"""

GUIA_FECHO = """  <aside class="glass-panel-violet mt-10 rounded-[2rem] p-6 sm:p-8">
    <p class="font-serif text-2xl font-bold text-white">Simule com o seu valor</p>
    <p class="mt-2 text-sm text-slate-300">Veja parcela, total na fatura, IOF e CET antes de decidir.</p>
    <p class="mt-5"><a href="/#simulador" class="inline-block rounded-2xl bg-violet-400 px-6 py-3 text-sm font-extrabold text-slate-950 hover:bg-violet-300">Abrir o simulador &rarr;</a></p>
  </aside>
  <section class="mt-10" aria-labelledby="veja-tambem">
    <h2 id="veja-tambem" class="text-sm font-bold uppercase tracking-widest text-white">Veja também</h2>
    <ul class="mt-4 grid gap-3 sm:grid-cols-3">@@RELACIONADOS@@</ul>
  </section>
"""
