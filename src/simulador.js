/* Interface do simulador. Só textContent e atributos SVG (nada de innerHTML). Depende de calculo.js (window.DatalabPix).
   Sem cookies e sem dado pessoal: só valor e prazo vão para a simulação do parceiro e para o Umami. */
(function () {
  'use strict';
  var P = window.DatalabPix;
  if (!P) return;

  var API = 'https://api.triagem.digital/proposals/simulator';
  var CHECKOUT = 'https://checkoutonline.digital/?l=' + P.tableUUID + '&u=ucHWD4k1tat4&lp=gyroo&wl=gyroo&s=';
  var LIMITE_MIN = 300;
  var LIMITE_MAX = 8000;
  var SVG = 'http://www.w3.org/2000/svg';

  var estado = { modo: 'valor', valor: 1000, limite: 2000, parcelas: 12 };
  var usou = false;
  var desenhos = 0;
  var timerUrl = null;
  var timerCopiado = null;
  var BRL_NUM = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 2 });
  var reduzMovimento = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function $(id) { return document.getElementById(id); }
  function clamp(v, a, b) { return Math.min(b, Math.max(a, v)); }
  function limpar(no) { while (no.firstChild) no.removeChild(no.firstChild); }
  function evento(nome, dados) {
    try { if (window.umami && window.umami.track) window.umami.track(nome, dados); } catch (e) { /* medição nunca quebra o simulador */ }
  }
  function svg(tag, attrs) {
    var e = document.createElementNS(SVG, tag);
    Object.keys(attrs).forEach(function (k) { e.setAttribute(k, attrs[k]); });
    return e;
  }

  function lerNumero(texto) {
    var t = String(texto).replace(/[^\d.,]/g, '');
    if (t.indexOf(',') >= 0) t = t.replace(/\./g, '').replace(',', '.');
    else if (/\.\d{3}(\.|$)/.test(t)) t = t.replace(/\./g, '');
    return Number(t);
  }

  function limiteNecessario(parcelas) {
    var T = P.tabela;
    return Math.ceil(P.PIX_MIN * (1 + T.fator_base + T.fator_por_parcela * parcelas));
  }

  function limitesDoCampo() {
    return estado.modo === 'valor' ? [P.PIX_MIN, P.PIX_MAX] : [LIMITE_MIN, LIMITE_MAX];
  }

  function desenharRosca(pix, total) {
    var alvo = $('donut');
    limpar(alvo);
    var r = 44;
    var circ = 2 * Math.PI * r;
    var parte = total > 0 ? (pix / total) * circ : 0;
    var s = svg('svg', { width: '120', height: '120', viewBox: '0 0 120 120', 'aria-hidden': 'true' });
    s.appendChild(svg('circle', { cx: '60', cy: '60', r: String(r), fill: 'none', stroke: '#f59e0b', 'stroke-width': '16' }));
    s.appendChild(svg('circle', {
      cx: '60', cy: '60', r: String(r), fill: 'none', stroke: '#8b5cf6', 'stroke-width': '16',
      'stroke-dasharray': parte.toFixed(2) + ' ' + (circ - parte).toFixed(2), transform: 'rotate(-90 60 60)'
    }));
    alvo.appendChild(s);
    var pct = total > 0 ? Math.round((pix / total) * 100) : 0;
    $('leg-pix').textContent = pct + '%';
    $('leg-custo').textContent = (100 - pct) + '% (' + P.brl(total - pix) + ')';
  }

  function desenharBarras(pix) {
    var alvo = $('barras');
    limpar(alvo);
    var linhas = [];
    var maior = 0;
    for (var n = 2; n <= 12; n++) {
      var c = P.simular('valor', pix, 0, n);
      linhas.push({ n: n, extra: c.total - pix, parcela: c.parcela });
      if (c.total - pix > maior) maior = c.total - pix;
    }
    linhas.forEach(function (l) {
      var b = document.createElement('button');
      b.type = 'button';
      var ativa = l.n === estado.parcelas;
      b.className = 'flex min-h-11 items-center gap-3 rounded-lg border px-3 py-2 text-left text-xs ' +
        (ativa ? 'border-violet-400/50 bg-violet-400/10 text-white' : 'border-transparent text-slate-300 hover:bg-white/5');
      b.setAttribute('aria-label', l.n + ' parcelas de ' + P.brl(l.parcela) + ', paga ' + P.brl(l.extra) + ' a mais');
      b.setAttribute('aria-pressed', String(ativa));
      var rot = document.createElement('span');
      rot.className = 'num w-7 shrink-0 font-bold';
      rot.textContent = l.n + 'x';
      var barra = svg('svg', { viewBox: '0 0 100 8', preserveAspectRatio: 'none', 'class': 'h-2 w-0 min-w-0 flex-1', 'aria-hidden': 'true' });
      barra.appendChild(svg('rect', { width: '100', height: '8', rx: '4', fill: '#1e293b' }));
      barra.appendChild(svg('rect', { width: (maior > 0 ? (l.extra / maior) * 100 : 0).toFixed(1), height: '8', rx: '4', fill: ativa ? '#a78bfa' : '#8b5cf6' }));
      var val = document.createElement('span');
      val.className = 'num w-24 shrink-0 text-right font-semibold';
      val.textContent = P.brl(l.extra);
      var parc = document.createElement('span');
      parc.className = 'num hidden w-28 shrink-0 text-right text-slate-400 sm:inline';
      parc.textContent = 'parcela ' + P.brl(l.parcela);
      b.appendChild(rot); b.appendChild(barra); b.appendChild(val); b.appendChild(parc);
      b.addEventListener('click', function () { estado.parcelas = l.n; interagiu(); desenhar(); });
      alvo.appendChild(b);
    });
    var minimo = linhas[0];
    var maximo = linhas[linhas.length - 1];
    $('txt-barras').textContent = 'Para receber ' + P.brl(pix) + ', você paga ' + P.brl(minimo.extra) + ' a mais em 2x e ' + P.brl(maximo.extra) +
      ' a mais em 12x: só ' + P.brl(maximo.extra - minimo.extra) + ' de diferença entre o prazo mais curto e o mais longo.';
  }

  function desenharTabela(pix) {
    $('cap-prazos').textContent = 'Para receber ' + P.brl(pix) + ' por Pix. Fonte: Tabela 10 do parceiro.';
    var corpo = $('corpo-prazos');
    limpar(corpo);
    for (var n = 2; n <= 12; n++) {
      var c = P.simular('valor', pix, 0, n);
      var ativa = n === estado.parcelas;
      var tr = document.createElement('tr');
      if (ativa) { tr.setAttribute('aria-current', 'true'); tr.className = 'bg-violet-400/10'; }
      [n + 'x', P.brl(c.parcela), P.brl(c.total), P.brl(c.total - pix), P.pct(c.jurosMes), P.pct(c.cetAno)].forEach(function (txt) {
        var td = document.createElement('td');
        td.className = 'num border-b border-white/10 px-3 py-2 ' + (ativa ? 'font-semibold text-white' : 'text-slate-300');
        td.textContent = txt;
        tr.appendChild(td);
      });
      corpo.appendChild(tr);
    }
  }

  // Compara os juros ao mês do Pix com as médias do Banco Central (juros com juros, nunca CET com juros). Sem dado, o bloco some.
  function desenharReferencia(r, escondido) {
    var refs = P.referencias || [];
    var bloco = $('referencia');
    if (!refs.length || escondido) { bloco.classList.add('hidden'); return; }
    bloco.classList.remove('hidden');
    var lista = $('ref-lista');
    limpar(lista);
    function linha(nome, valor, destaque) {
      var li = document.createElement('li');
      li.className = 'flex items-baseline justify-between gap-3 ' + (destaque ? 'font-semibold text-violet-300' : 'text-slate-300');
      var a = document.createElement('span');
      a.textContent = nome;
      var b = document.createElement('span');
      b.className = 'num shrink-0';
      b.textContent = valor;
      li.appendChild(a); li.appendChild(b);
      lista.appendChild(li);
    }
    linha('Pix no cartão em ' + estado.parcelas + 'x', P.pct(r.jurosMes) + ' ao mês', true);
    var meses = [];
    refs.forEach(function (x) {
      linha(x.nome + ' (média)', P.pct(x.am) + ' ao mês', false);
      if (meses.indexOf(x.mes) < 0) meses.push(x.mes);
    });
    var menores = refs.filter(function (x) { return x.am < r.jurosMes * 0.97; });
    var texto;
    if (menores.length === refs.length) {
      texto = 'Em média, as ' + refs.length + ' modalidades acima têm juros menores que o Pix em ' + estado.parcelas + 'x. Peça o CET dessas alternativas antes de decidir.';
    } else if (menores.length === 0) {
      texto = 'Nenhuma das médias acima tem juros claramente menores que o Pix em ' + estado.parcelas + 'x.';
    } else {
      var nomes = menores.map(function (x) { return x.nome.toLowerCase(); }).join(' e ');
      texto = 'Em média, ' + nomes + (menores.length > 1 ? ' têm' : ' tem') + ' juros menores que o Pix em ' + estado.parcelas + 'x. Peça o CET dessas alternativas antes de decidir.';
    }
    $('ref-veredito').textContent = texto;
    $('ref-nota').textContent = 'Média das novas operações de crédito de pessoas físicas (Banco Central, ' + meses.join(' e ') +
      '). É taxa de juros, não é CET, e não é oferta: a sua pode ser maior ou menor.';
  }

  // Endereço compartilhável: modo, valor (ou limite) e parcelas. Sem dado pessoal. O canonical da página continua sendo a home.
  function lerEndereco() {
    try {
      var q = new URLSearchParams(window.location.search);
      var modo = q.get('modo');
      if (modo === 'valor' || modo === 'limite') estado.modo = modo;
      var par = parseInt(q.get('parcelas'), 10);
      if (par >= 2 && par <= 12) estado.parcelas = par;
      var soNumero = /^[\d.,]+$/;  // qualquer outra coisa no endereço é ignorada
      var tv = q.get('valor') || '';
      var v = soNumero.test(tv) ? lerNumero(tv) : 0;
      if (v > 0) estado.valor = clamp(v, P.PIX_MIN, P.PIX_MAX);
      var tl = q.get('limite') || '';
      var l = soNumero.test(tl) ? lerNumero(tl) : 0;
      if (l > 0) estado.limite = clamp(l, LIMITE_MIN, LIMITE_MAX);
    } catch (e) { /* endereço estranho: usa os valores padrão */ }
  }

  function enderecoDaSimulacao() {
    var q = new URLSearchParams();
    var campo = estado.modo === 'valor' ? estado.valor : estado.limite;
    q.set('modo', estado.modo);
    q.set(estado.modo, String(Math.round(campo * 100) / 100));
    q.set('parcelas', String(estado.parcelas));
    return window.location.origin + window.location.pathname + '?' + q.toString() + '#simulador';
  }

  function atualizarEndereco() {
    clearTimeout(timerUrl);
    // espera a pessoa parar de mexer: o navegador limita as trocas de endereço por segundo
    timerUrl = setTimeout(function () {
      try { window.history.replaceState(null, '', enderecoDaSimulacao()); } catch (e) { /* sem histórico: o botão de copiar continua valendo */ }
    }, 400);
  }

  async function copiarLink() {
    var url = enderecoDaSimulacao();
    var ok = false;
    try { window.history.replaceState(null, '', url); } catch (e) { /* ignora */ }
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) { await navigator.clipboard.writeText(url); ok = true; }
    } catch (e) { /* tenta o plano B abaixo */ }
    if (!ok) {
      try {
        var t = document.createElement('textarea');
        t.value = url;
        t.setAttribute('readonly', '');
        t.className = 'fixed left-0 top-0 opacity-0';
        document.body.appendChild(t);
        t.select();
        ok = document.execCommand('copy');
        document.body.removeChild(t);
      } catch (e) { ok = false; }
    }
    var msg = $('msg-copiado');
    msg.textContent = ok ? 'Link copiado. Quem abrir vê esta mesma simulação.' : 'Não deu para copiar sozinho. O link já está na barra de endereço do navegador.';
    msg.classList.remove('hidden');
    clearTimeout(timerCopiado);
    timerCopiado = setTimeout(function () { msg.classList.add('hidden'); }, 4000);
    evento('copiou-link', { valor: estado.modo === 'valor' ? estado.valor : estado.limite, prazo: estado.parcelas, modo: estado.modo });
  }

  function desenhar() {
    var r = P.simular(estado.modo, estado.valor, estado.limite, estado.parcelas);
    var lim = limitesDoCampo();
    var campo = estado.modo === 'valor' ? estado.valor : estado.limite;
    var abaixo = estado.modo === 'limite' && r.pix < P.PIX_MIN;

    $('rotulo-valor').textContent = estado.modo === 'valor' ? 'Valor que você quer no Pix' : 'Limite disponível no cartão';
    $('range-valor').min = lim[0]; $('range-valor').max = lim[1];
    $('range-valor').value = clamp(campo, lim[0], lim[1]);
    $('range-valor').setAttribute('aria-valuetext', P.brl(Number($('range-valor').value)));
    if (document.activeElement !== $('campo-valor')) $('campo-valor').value = BRL_NUM.format(campo);
    $('min-valor').textContent = P.brl(lim[0]);
    $('max-valor').textContent = P.brl(lim[1]);
    $('range-parcelas').value = estado.parcelas;
    $('range-parcelas').setAttribute('aria-valuetext', estado.parcelas + ' parcelas');
    $('txt-parcelas').textContent = estado.parcelas + 'x';

    var ehValor = estado.modo === 'valor';
    $('btn-modo-valor').setAttribute('aria-selected', String(ehValor));
    $('btn-modo-limite').setAttribute('aria-selected', String(!ehValor));
    $('btn-modo-valor').tabIndex = ehValor ? 0 : -1;
    $('btn-modo-limite').tabIndex = ehValor ? -1 : 0;
    $('painel-simulacao').setAttribute('aria-labelledby', ehValor ? 'btn-modo-valor' : 'btn-modo-limite');

    $('r-pix').textContent = P.brl(r.pix);
    $('r-parcelas').textContent = estado.parcelas + ' parcelas de ' + P.brl(r.parcela);
    $('r-total').textContent = P.brl(r.total);
    $('r-iof').textContent = P.brl(r.iof);
    $('r-juros').textContent = P.pct(r.jurosMes);
    $('r-cet').textContent = P.pct(r.cetAno);
    $('r-custo-texto').textContent = 'Você recebe ' + P.brl(r.pix) + ' e paga ' + P.brl(r.total) +
      ' na fatura: ' + P.brl(r.total - r.pix) + ' a mais, com juros e IOF.';
    $('aviso-minimo').classList.toggle('hidden', !abaixo);
    if (abaixo) {
      $('aviso-minimo').textContent = 'Com esse limite, o Pix ficaria abaixo do mínimo de ' + P.brl(P.PIX_MIN) + '. Em ' + estado.parcelas +
        'x, você precisa de um limite de pelo menos ' + P.brl(limiteNecessario(estado.parcelas)) + ', ou diminua as parcelas.';
    }
    $('cta-pix').disabled = abaixo;
    $('resumo-parcela').textContent = abaixo ? 'Limite abaixo do mínimo' : estado.parcelas + 'x de ' + P.brl(r.parcela);
    $('resumo-total').textContent = abaixo ? 'Aumente o limite ou diminua as parcelas' : 'Total na fatura ' + P.brl(r.total);

    desenharRosca(r.pix, r.total);
    desenharBarras(r.pix);
    desenharReferencia(r, abaixo);
    desenharTabela(r.pix);
    desenhos += 1;
    if (desenhos > 1) atualizarEndereco();  // o primeiro desenho é o da carga da página
  }

  function interagiu() {
    if (usou) return;
    usou = true;
    evento('usou-simulador-pix', { valor: estado.modo === 'valor' ? estado.valor : estado.limite, prazo: estado.parcelas });
  }

  function definirCampo(v) {
    var lim = limitesDoCampo();
    if (estado.modo === 'valor') estado.valor = clamp(v, lim[0], lim[1]); else estado.limite = clamp(v, lim[0], lim[1]);
  }

  async function abrirProposta() {
    var btn = $('cta-pix');
    if (btn.disabled) return;
    btn.disabled = true;
    var rotulo = btn.textContent;
    $('aviso-proposta').classList.add('hidden');
    btn.textContent = 'Abrindo sua proposta...';
    evento('cta-pix', { valor: estado.modo === 'valor' ? estado.valor : estado.limite, prazo: estado.parcelas, modo: estado.modo });
    var corpo = { parcels: estado.parcelas, tableUUID: P.tableUUID };
    if (estado.modo === 'valor') corpo.desiredValue = estado.valor; else corpo.limitValue = estado.limite;
    var uuid = null;
    try {
      var ctl = new AbortController();
      var t = setTimeout(function () { ctl.abort(); }, 8000);
      var resp = await fetch(API, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(corpo), signal: ctl.signal });
      clearTimeout(t);
      if (resp.ok) {
        var dados = await resp.json();
        if (dados && dados.uuid) uuid = dados.uuid;
      }
    } catch (e) { /* tratado abaixo: sem simulação do parceiro não há pré-preenchimento */ }
    if (!uuid) {
      // não manda a pessoa para o parceiro achando que a proposta foi preenchida: avisa e deixa escolher
      var valorTxt = estado.modo === 'valor' ? P.brl(estado.valor) + ' no Pix' : 'limite de ' + P.brl(estado.limite);
      $('txt-aviso-proposta').textContent = 'Não conseguimos pré-preencher a proposta agora. Você pode tentar de novo ou continuar no parceiro e informar lá ' +
        valorTxt + ' em ' + estado.parcelas + 'x.';
      $('link-parceiro').href = CHECKOUT;
      $('aviso-proposta').classList.remove('hidden');
      evento('cta-pix-sem-preenchimento', { prazo: estado.parcelas, modo: estado.modo });
      btn.disabled = false;
      btn.textContent = rotulo;
      return;
    }
    var destino = CHECKOUT + encodeURIComponent(uuid);
    // dá tempo de o evento do Umami sair antes de trocar de página
    await new Promise(function (r) { setTimeout(r, 350); });
    window.location.href = destino;
    setTimeout(function () { btn.disabled = false; btn.textContent = rotulo; }, 3000);
  }

  // Barra fixa no celular: enquanto a pessoa mexe nos controles e o resultado está fora da tela, mostra parcela e total.
  function iniciarBarraResumo() {
    var barra = $('barra-resumo');
    if (!barra || !('IntersectionObserver' in window)) return;
    var vendo = { simulador: false, resultado: false };
    function atualizar() { barra.classList.toggle('hidden', !(vendo.simulador && !vendo.resultado)); }
    var obs = new IntersectionObserver(function (itens) {
      itens.forEach(function (i) { vendo[i.target.id === 'simulador' ? 'simulador' : 'resultado'] = i.isIntersecting; });
      atualizar();
    });
    obs.observe($('simulador'));
    obs.observe($('resultado'));
    $('btn-resumo').addEventListener('click', function () {
      $('resultado').scrollIntoView({ behavior: reduzMovimento ? 'auto' : 'smooth', block: 'center' });
    });
  }

  function iniciar() {
    lerEndereco();
    $('btn-modo-valor').addEventListener('click', function () { estado.modo = 'valor'; desenhar(); });
    $('btn-modo-limite').addEventListener('click', function () { estado.modo = 'limite'; desenhar(); });
    $('btn-modo-valor').parentNode.addEventListener('keydown', function (e) {
      var ir = { ArrowLeft: 'valor', ArrowRight: 'limite', Home: 'valor', End: 'limite' }[e.key];
      if (!ir) return;
      e.preventDefault();
      estado.modo = ir;
      desenhar();
      $(ir === 'valor' ? 'btn-modo-valor' : 'btn-modo-limite').focus();
    });
    $('range-valor').addEventListener('input', function (e) { definirCampo(Number(e.target.value)); interagiu(); desenhar(); });
    $('campo-valor').addEventListener('input', function (e) {
      // enquanto digita, só atualiza com valor dentro da faixa: "1", "15", "150" a caminho de 1500 não derrubam o resultado para o mínimo
      var v = lerNumero(e.target.value);
      if (v >= limitesDoCampo()[0]) { definirCampo(v); interagiu(); desenhar(); }
    });
    $('campo-valor').addEventListener('blur', function (e) {
      var v = lerNumero(e.target.value);
      if (v > 0) { definirCampo(v); interagiu(); }
      desenhar();
      e.target.value = BRL_NUM.format(estado.modo === 'valor' ? estado.valor : estado.limite);  // mostra o valor já ajustado à faixa
    });
    $('campo-valor').addEventListener('keydown', function (e) { if (e.key === 'Enter') e.target.blur(); });
    $('range-parcelas').addEventListener('input', function (e) { estado.parcelas = Number(e.target.value); interagiu(); desenhar(); });
    $('cta-pix').addEventListener('click', abrirProposta);
    $('btn-copiar').addEventListener('click', copiarLink);
    iniciarBarraResumo();
    var pc = window.matchMedia && window.matchMedia('(pointer: fine) and (min-width: 900px)').matches;
    $('aviso-celular').classList.toggle('hidden', !pc);
    desenhar();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})();
