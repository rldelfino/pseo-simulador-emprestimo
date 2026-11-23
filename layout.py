"""HTML do layout (cabeçalho, rodapé), da home e dos blocos dos guias. Os marcadores @@NOME@@ são trocados pelo gerador.

Mesmo template dos simuladores irmãos (Home Equity, Auto Equity, Condomínio): tema escuro, vidro, cartões por campo, painel de resultado, faixa de
3 números, campo "já tem uma proposta?" e tela de confirmação antes do parceiro. Destaque roxo (violet). CSS à mão em src/estilo.css (sem build).
Sem atributo style nem script inline (a CSP não permite). Os desenhos de barras são SVG com atributos; a lógica fica em src/simulador.js.
"""

# Marca da Datalab Global padronizada com os simuladores irmãos (a mesma do Home Equity): frasco com órbita e barras. Cor pelo --ac (roxo neste site).
LOGO = """<span class="tile"><svg viewBox="0 0 44 44" width="32" height="32" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><ellipse cx="22" cy="29" rx="19" ry="6.2" transform="rotate(-22 22 29)" stroke-width="1.3" opacity=".6"/><path d="M17.5 11.5h9M18.8 11.5V22L9.7 37.6a2.3 2.3 0 0 0 2 3.4h20.6a2.3 2.3 0 0 0 2-3.4L25.2 22V11.5" stroke-width="2"/><g fill="currentColor" stroke="none"><rect x="16" y="34" width="2.2" height="4.6" rx=".6"/><rect x="19.6" y="31" width="2.2" height="7.6" rx=".6"/><rect x="23.2" y="33" width="2.2" height="5.6" rx=".6"/><rect x="26.8" y="29.5" width="2.2" height="9.1" rx=".6"/><rect x="19.4" y="6.6" width="1.7" height="3.4" rx=".5"/><rect x="22.4" y="5" width="1.7" height="5" rx=".5"/><rect x="25.4" y="3.6" width="1.7" height="6.4" rx=".5"/><circle cx="31" cy="9.5" r="1.3"/><circle cx="35.5" cy="5.6" r="1.3"/></g><path d="M31 9.5l4.5-3.9" stroke-width="1.3"/></svg></span>"""

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
<link rel="alternate" type="application/atom+xml" title="Empréstimo pessoal com crédito do cartão — Datalab Global" href="/feed.xml">
@@JSONLD@@<script defer src="https://cloud.umami.is/script.js" data-website-id="@@UMAMI_ID@@"></script>
</head>
<body>
<a href="#conteudo" class="skip">Ir para o conteúdo</a>
<header class="top">
  <div class="wrap">
    <span class="bk"><a href="https://www.datalabglobal.com/" class="brand" aria-label="Datalab Global, site principal">@@LOGO@@<span class="wm"><b>Datalab</b><i>GLOBAL</i></span></a><a href="/" class="prod" aria-label="Empréstimo pessoal com crédito do cartão, página inicial do simulador"><span class="pl">Empréstimo com crédito do cartão</span><span class="pc">Empréstimo com cartão</span></a></span>
    <nav class="m" aria-label="Principal">@@NAV@@</nav>
    <div class="free"><span class="dot"></span>Simulação gratuita</div>
    <details class="menu">
      <summary>Menu</summary>
      <nav aria-label="Menu">@@NAVMOBILE@@</nav>
    </details>
  </div>
</header>

<main id="conteudo" class="wrap">
@@MAIN@@
</main>

<footer class="rod">
  <div class="wrap">
    <div class="cols">
      <div>
        <a href="https://www.datalabglobal.com/" class="brand" aria-label="Datalab Global, site principal">@@LOGO@@<span class="wm"><b>Datalab</b><i>GLOBAL</i></span></a>
        <p>Simulador do empréstimo pessoal com crédito do cartão. O custo aparece antes de qualquer botão.</p>
        <p>Não somos banco e não concedemos crédito.</p>
      </div>
      <nav aria-label="Entenda"><h2>Entenda</h2><ul>@@FOOT_ENTENDA@@</ul></nav>
      <nav aria-label="Transparência"><h2>Transparência</h2><ul>@@FOOT_TRANSP@@</ul></nav>
      <nav aria-label="Legal e mais"><h2>Legal e mais</h2><ul>@@FOOT_LEGAL@@</ul></nav>
      <nav aria-label="Outros simuladores da Datalab Global"><h2>Outros simuladores</h2><ul>@@FOOT_OUTROS@@</ul></nav>
    </div>
    <div class="base">
      <p>Atualizado em @@ATUALIZADO@@. Condições da Tabela 10 do parceiro, conferidas automaticamente toda semana.</p>
      <p>Datalab Global é marca de @@RAZAO@@, CNPJ @@CNPJ@@. Contato: <a href="mailto:@@EMAIL@@">@@EMAIL@@</a>.</p>
      <p>A simulação não é proposta de crédito. Crédito sujeito a análise e aprovação do parceiro, sem garantia de aprovação.</p>
    </div>
  </div>
</footer>
@@SCRIPTS@@</body>
</html>
"""

HOME_MAIN = """  <section class="hero">
    <h1>Empréstimo pessoal com <em>crédito do cartão</em></h1>
    <p>Use o limite do cartão de crédito como fonte do dinheiro: receba de <strong>R$ 300 a R$ 5.000</strong> por Pix e pague em <strong>2x a 12x</strong> na fatura. O custo aparece primeiro, antes de qualquer botão.</p>
    <div class="fine">Grátis · sem cadastro · estimativa, não proposta · atualizado em @@ATUALIZADO@@</div>
  </section>

  <div class="grid" id="simulador">
    <section class="panel" aria-labelledby="t-cenario">
      <h2 id="t-cenario">Seu cenário</h2>
      <div role="tablist" class="segt" aria-label="Como você quer simular">
        <button id="btn-modo-valor" type="button" role="tab" aria-selected="true" aria-controls="painel-simulacao">Quero um valor<small>quanto cai na conta</small></button>
        <button id="btn-modo-limite" type="button" role="tab" aria-selected="false" tabindex="-1" aria-controls="painel-simulacao">Usar meu limite<small>quanto tenho no cartão</small></button>
      </div>
      <div id="painel-simulacao" role="tabpanel" aria-labelledby="btn-modo-valor" class="pnl">
        <div class="f">
          <label id="rotulo-valor" for="campo-valor">Valor que você quer receber <span id="sub-valor">cai na conta, por Pix</span></label>
          <div class="inp"><span class="pre">R$</span><input id="campo-valor" type="text" inputmode="decimal" autocomplete="off" value="@@D_VALOR@@" class="num"></div>
          <input id="range-valor" data-p="15" aria-labelledby="rotulo-valor" type="range" min="300" max="5000" step="50" value="@@D_VALOR_N@@">
          <div class="slabel"><span id="min-valor">R$ 300,00</span><span id="max-valor">R$ 5.000,00</span></div>
        </div>
        <div class="f">
          <label for="range-parcelas">Parcelas na fatura <span>de 2x a 12x</span></label>
          <div class="inp"><strong id="txt-parcelas" class="nv num">12x</strong></div>
          <input id="range-parcelas" data-p="100" type="range" min="2" max="12" step="1" value="12">
          <div class="slabel"><span>2x</span><span>12x</span></div>
        </div>
      </div>
      <details class="outra" id="det-prop">
        <summary>Já tem uma proposta? Compare a taxa dela</summary>
        <div class="oi">
          <label for="campo-prop">Parcela da proposta <span>R$ por mês</span></label>
          <div class="inp"><span class="pre">R$</span><input id="campo-prop" type="text" inputmode="decimal" autocomplete="off" placeholder="ex.: 150,00" class="num" aria-describedby="msg-prop"><em>/mês</em></div>
          <div class="hint" id="msg-prop">Usa o valor que você recebe e o número de parcelas escolhidos acima. Informe a parcela que aparece na proposta e veja quanto ela cobra de juros ao mês.</div>
        </div>
      </details>
      <div class="note limnote"><b>E o limite do cartão?</b> <span id="nota-limite">@@D_NOTA_LIMITE@@</span> <a href="#o-que-e">Entenda</a></div>
    </section>

    <section class="panel resp" id="resultado" aria-labelledby="t-resultado" aria-live="polite">
      <h2 class="kicker kres" id="t-resultado">Resultado da simulação</h2>
      <div class="res">
        <div>
          <div class="kicker" id="r-kicker">Parcela na fatura</div>
          <div class="big num"><span id="r-parcela">@@D_PARCELA@@</span> <small>/mês</small></div>
          <div class="dim" id="r-sub">@@D_SUB@@</div>
          <hr class="sep">
          <div class="dim lab">Total na fatura</div>
          <div class="mid num" id="r-total">@@D_TOTAL@@</div>
          <div class="dim"><a href="/metodologia">Como calculamos</a></div>
        </div>
        <div class="ctx sis">
          <div class="t">Você recebe por Pix</div>
          <div class="v num" id="r-receber">@@D_RECEBER@@</div>
          <div class="t">IOF (já incluso)</div>
          <div class="v num" id="r-iof">@@D_IOF@@</div>
        </div>
      </div>
      <div class="callout"><p id="r-resumo">@@D_RESUMO@@</p></div>
      <div class="rosca">
        <svg viewBox="0 0 120 120" width="120" height="120" role="img" id="donut" aria-label="Do total na fatura, @@D_PCT_CUSTO@@% é juros e IOF">
          <circle cx="60" cy="60" r="46" fill="none" stroke="#e3a96b" stroke-width="14"/>
          <circle id="rosca-valor" cx="60" cy="60" r="46" fill="none" stroke="#a78bfa" stroke-width="14" stroke-dasharray="@@D_ROSCA_P@@ 289.03" transform="rotate(-90 60 60)"/>
          <text x="60" y="61" text-anchor="middle" class="rc-n" id="rosca-pct">@@D_PCT_CUSTO@@%</text>
          <text x="60" y="77" text-anchor="middle" class="rc-t">em juros e IOF</text>
        </svg>
        <div class="rc-l">
          <div class="kicker">Para onde vai o total</div>
          <div class="lg"><span><s></s>Valor que você recebe</span><b class="num" id="leg-valor">@@D_L_VALOR@@</b></div>
          <div class="lg"><span><s class="jr"></s>Juros e IOF</span><b class="num" id="leg-custo">@@D_L_CUSTO@@</b></div>
        </div>
      </div>
      <div class="rodape-res">
        <p id="aviso-minimo" class="hint warn" hidden>Com esse limite, o valor ficaria abaixo do mínimo de R$ 300.</p>
        <div class="cta">
          <div><strong>Faça sua proposta</strong><span class="s">Com um parceiro de crédito · pedido real, 6 passos</span></div>
          <button type="button" class="btn" id="btn-cta">Ver minha proposta →</button>
        </div>
        <div class="fine2">Estimativa: a aprovação e o valor final dependem da análise do parceiro. O total é lançado no limite do seu cartão: <a href="#o-que-e">entenda abaixo</a>.</div>
        <div class="copiar"><button type="button" id="btn-copiar">Copiar o link desta simulação</button><span id="msg-copiado" role="status"></span></div>
      </div>
    </section>
  </div>

  <div class="kpis" aria-label="Três números para ler o custo">
    <div class="kp"><span class="t">Juros ao mês</span><b class="num" id="r-juros">@@D_JUROS@@</b><small>Tabela 10 do parceiro</small></div>
    <div class="kp"><span class="t">CET ao ano</span><b class="num" id="r-cet">@@D_CET@@</b><small>inclui o IOF, para comparar</small></div>
    <div class="kp"><span class="t">Cada R$ 1 recebido custa</span><b class="num" id="k-real">@@D_REAL@@</b><small>na fatura, com juros e IOF</small></div>
  </div>
  <p class="hint kpn">Juros e CET da Tabela 10 do parceiro, conferida toda semana. Estimativa, não é oferta. <a href="/custo-cet-iof">Veja a tabela completa</a>.</p>

  <section class="band" id="o-que-e" aria-labelledby="t-oqe">
    <div class="split">
      <div class="split-t">
        <div class="kicker">O que é</div>
        <h2 id="t-oqe">Um empréstimo pessoal que usa o limite do cartão</h2>
        <p class="lead">@@O_QUE_E@@</p>
        <p class="hint"><a href="/como-funciona">Veja o passo a passo completo</a></p>
      </div>
      <div class="lista3">
        <div class="li3"><span class="n" aria-hidden="true">1</span><div><h3>Você pede um valor</h3><ul><li>De R$ 300 a R$ 5.000, por Pix, em uma chave em seu nome</li><li>O Pix é só o jeito de o dinheiro chegar à sua conta</li></ul></div></div>
        <div class="li3"><span class="n" aria-hidden="true">2</span><div><h3>O total vai para o limite do cartão</h3><ul><li>Valor, juros e IOF ficam comprometidos no limite</li><li>É por isso que existe o modo “Usar meu limite”</li></ul></div></div>
        <div class="li3"><span class="n" aria-hidden="true">3</span><div><h3>Você paga na fatura</h3><ul><li>De 2 a 12 parcelas, junto com o resto da fatura</li><li>Como o limite é liberado conforme você paga é regra do emissor do cartão</li></ul></div></div>
      </div>
    </div>
  </section>

  <section class="blk" id="prazos" aria-labelledby="t-prazos">
    <div class="kicker">Prazo</div>
    <h2 id="t-prazos">O custo quase não muda com o prazo</h2>
    <div class="split pzsplit">
      <div class="panel">
        <div class="kicker pzk">Quanto você paga a mais, em reais, por prazo</div>
        <div id="barras" class="pzs"></div>
      </div>
      <div class="pztx">
        <p id="txt-barras"></p>
        <p>Prazo maior deixa a prestação menor, mas o dinheiro fica emprestado por mais tempo. O que pesa de verdade é o valor em reais da barra.</p>
        <p class="hint"><a href="/custo-cet-iof">Entenda CET e IOF</a> · <a href="/@@SLUG_COMPARAR@@">Compare com outros créditos</a></p>
      </div>
    </div>
    <details id="detalhe-prazos" class="amort">
      <summary>Ver a tabela de todos os prazos (2x a 12x)</summary>
      <div class="tw"><table class="tc">
        <caption id="cap-prazos"></caption>
        <thead><tr><th scope="col">Prazo</th><th scope="col">Parcela</th><th scope="col">Total na fatura</th><th scope="col">Custo a mais</th><th scope="col">Juros ao mês</th><th scope="col">CET ao ano</th></tr></thead>
        <tbody id="corpo-prazos"></tbody>
      </table></div>
    </details>
  </section>

  <section class="blk" aria-labelledby="t-mercado">
    <div class="kicker">Mercado</div>
    <h2 id="t-mercado">E as outras opções de crédito?</h2>
    <p class="lead">@@COMPARA@@</p>
    <div id="referencia" class="panel refp" hidden aria-live="off">
      <div class="kicker">Juros ao mês, hoje</div>
      <ul id="ref-lista" class="reflist"></ul>
      <p id="ref-veredito" class="refv"></p>
      <p id="ref-nota" class="hint"></p>
      <p class="hint"><a href="/taxas-de-referencia">Ver as taxas do Banco Central e a fonte</a></p>
    </div>
  </section>

  <section class="blk dois" aria-label="Custo e quem oferece">
    <div class="card"><h3>Quanto custa, de verdade</h3>
      <p>@@CUSTO_HOME@@ Se você consegue outra forma de crédito mais barata, ela costuma valer mais a pena. <a href="/custo-cet-iof">Veja a tabela completa</a>.</p></div>
    <div class="card"><h3>Quem oferece</h3>
      <p>A oferta é de um correspondente bancário parceiro. O contrato é uma Cédula de Crédito Bancário (CCB), e a aprovação depende de análise de crédito: não há garantia de aprovação nem de valor. <a href="/sobre">Saiba mais</a>.</p></div>
  </section>

  <section class="blk" aria-labelledby="t-guias">
    <div class="kicker">Guias</div>
    <h2 id="t-guias">Entenda antes de decidir</h2>
    <div class="cols3">@@CARTOES@@</div>
  </section>

  <section class="blk split faqs" aria-labelledby="t-faq">
    <div class="split-t">
      <div class="kicker">Dúvidas</div>
      <h2 id="t-faq">Perguntas frequentes</h2>
    </div>
    <div class="faq">@@FAQ@@</div>
  </section>

  <aside class="fecho fechohome">
    <p class="t">Compare o custo e só então peça a proposta.</p>
    <p>A contratação é feita no ambiente de um parceiro (correspondente bancário) e depende de análise de crédito. Sem garantia de aprovação.</p>
    <a class="btn" href="#simulador">Voltar ao simulador</a>
  </aside>

  <div id="barra-resumo" class="barra-res" hidden>
    <button id="btn-resumo" type="button">
      <span class="bt"><span id="resumo-parcela" class="num"></span><span id="resumo-total" class="num sub"></span></span>
      <span class="go">Ver resultado ↓</span>
    </button>
  </div>

  <dialog id="dlg-confirma" aria-labelledby="dlg-titulo">
    <h3 id="dlg-titulo">Antes de continuar</h3>
    <p>Você vai pedir um <b>empréstimo pessoal com crédito do cartão</b> a um <b>parceiro de crédito</b>, que analisa o seu pedido. A página dele mostra o nome da empresa.</p>
    <ul>
      <li id="dlg-resumo">@@D_DLG_RESUMO@@</li>
      <li>O total é lançado no limite do seu cartão e parcelado na fatura.</li>
      <li>É um pedido real: 6 passos, com CPF e documento original (RG ou CNH).</li>
      <li>A aprovação e o valor final dependem da análise do parceiro. Simular aqui não é aprovação e você não é obrigado a contratar.</li>
      <li id="aviso-celular" hidden>No computador, a tela do parceiro mostra um QR Code: aponte a câmera do celular para continuar por lá. Tenha o RG ou a CNH original em mãos.</li>
    </ul>
    <div id="aviso-proposta" class="hint warn" hidden>
      <span id="txt-aviso-proposta"></span>
      <a id="link-parceiro" href="@@CHECKOUT@@" rel="noopener sponsored">Continuar mesmo assim →</a>
    </div>
    <p class="dim">Este site envia ao parceiro só o valor e o prazo. Veja a <a href="/privacidade">política de privacidade</a> e <a href="/metodologia">como calculamos</a>.</p>
    <div class="row"><button type="button" class="btn" id="btn-parceiro">Continuar para o parceiro →</button><button type="button" class="ghost" id="btn-voltar">Voltar e ajustar</button></div>
  </dialog>
"""

GUIA_CABECALHO = """<div class="volta"><a class="btn-volta" href="/#simulador" data-volta>← Voltar à simulação</a></div>
<nav class="crumb" aria-label="Você está em"><a href="/">Empréstimo com crédito do cartão <span>@@ROTULO_PAGINA@@</span></a></nav>
<article class="guia">
  <h1>@@H1@@</h1>
  <p class="meta">Atualizado em @@ATUALIZADO@@ · @@RAZAO@@</p>
  <div class="prose">
"""

GUIA_MEIO = """  </div>
"""

GUIA_FECHO = """  <aside class="fecho">
    <p class="t">Simule com o seu valor</p>
    <p>Veja parcela, total na fatura, IOF e CET antes de decidir.</p>
    <a class="btn" href="/#simulador" data-volta>Voltar à simulação →</a>
  </aside>
  <section class="rel" aria-labelledby="veja-tambem">
    <h2 id="veja-tambem">Veja também</h2>
    <ul>@@RELACIONADOS@@</ul>
  </section>
"""
