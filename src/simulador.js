/* Interface do simulador. Só textContent e atributos SVG (nada de innerHTML). Depende de calculo.js (window.DatalabPix).
   Sem cookies e sem dado pessoal: só valor e prazo vão para a simulação do parceiro e para o Umami. */
(function () {
  'use strict';
  var P = window.DatalabPix;
  if (!P) return;

  var API = 'https://api.triagem.digital/proposals/simulator';
  var CHECKOUT = 'https://checkoutonline.digital/?l=' + P.tableUUID + '&u=ucHWD4k1tat4&lp=gyroo&wl=gyroo&s=';
  var LIMITE_MIN = 500;
  var LIMITE_MAX = 8000;
  var SVG = 'http://www.w3.org/2000/svg';

  var estado = { modo: 'valor', valor: 1000, limite: 2000, parcelas: 12 };
  var usou = false;

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
      cx: '60', cy: '60', r: String(r), fill: 'none', stroke: '#10b981', 'stroke-width': '16',
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
      b.className = 'flex items-center gap-3 rounded-lg border px-3 py-2 text-left text-xs ' +
        (ativa ? 'border-emerald-400/50 bg-emerald-400/10 text-white' : 'border-transparent text-slate-300 hover:bg-white/5');
      b.setAttribute('aria-label', l.n + ' parcelas de ' + P.brl(l.parcela) + ', paga ' + P.brl(l.extra) + ' a mais');
      b.setAttribute('aria-pressed', String(ativa));
      var rot = document.createElement('span');
      rot.className = 'num w-7 shrink-0 font-bold';
      rot.textContent = l.n + 'x';
      var barra = svg('svg', { viewBox: '0 0 100 8', preserveAspectRatio: 'none', 'class': 'h-2 w-0 min-w-0 flex-1', 'aria-hidden': 'true' });
      barra.appendChild(svg('rect', { width: '100', height: '8', rx: '4', fill: '#1e293b' }));
      barra.appendChild(svg('rect', { width: (maior > 0 ? (l.extra / maior) * 100 : 0).toFixed(1), height: '8', rx: '4', fill: ativa ? '#34d399' : '#10b981' }));
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

  function desenhar() {
    var r = P.simular(estado.modo, estado.valor, estado.limite, estado.parcelas);
    var lim = limitesDoCampo();
    var campo = estado.modo === 'valor' ? estado.valor : estado.limite;
    var abaixo = estado.modo === 'limite' && r.pix < P.PIX_MIN;

    $('rotulo-valor').textContent = estado.modo === 'valor' ? 'Valor que você quer no Pix' : 'Limite disponível no cartão';
    $('range-valor').min = lim[0]; $('range-valor').max = lim[1];
    $('range-valor').value = clamp(campo, lim[0], lim[1]);
    $('campo-valor').min = lim[0]; $('campo-valor').max = lim[1];
    if (document.activeElement !== $('campo-valor')) $('campo-valor').value = campo;
    $('min-valor').textContent = P.brl(lim[0]);
    $('max-valor').textContent = P.brl(lim[1]);
    $('range-parcelas').value = estado.parcelas;
    $('txt-parcelas').textContent = estado.parcelas + 'x';

    $('btn-modo-valor').setAttribute('aria-selected', String(estado.modo === 'valor'));
    $('btn-modo-limite').setAttribute('aria-selected', String(estado.modo === 'limite'));

    $('r-pix').textContent = P.brl(r.pix);
    $('r-parcelas').textContent = estado.parcelas + ' parcelas de ' + P.brl(r.parcela);
    $('r-total').textContent = P.brl(r.total);
    $('r-iof').textContent = P.brl(r.iof);
    $('r-juros').textContent = P.pct(r.jurosMes);
    $('r-cet').textContent = P.pct(r.cetAno);
    $('r-custo-texto').textContent = 'Você recebe ' + P.brl(r.pix) + ' e paga ' + P.brl(r.total) +
      ' na fatura: ' + P.brl(r.total - r.pix) + ' a mais, com juros e IOF.';
    $('aviso-minimo').classList.toggle('hidden', !abaixo);
    $('cta-pix').disabled = abaixo;

    desenharRosca(r.pix, r.total);
    desenharBarras(r.pix);
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
    btn.textContent = 'Abrindo sua proposta...';
    evento('cta-pix', { valor: estado.modo === 'valor' ? estado.valor : estado.limite, prazo: estado.parcelas, modo: estado.modo });
    var corpo = { parcels: estado.parcelas, tableUUID: P.tableUUID };
    if (estado.modo === 'valor') corpo.desiredValue = estado.valor; else corpo.limitValue = estado.limite;
    var destino = CHECKOUT;
    try {
      var ctl = new AbortController();
      var t = setTimeout(function () { ctl.abort(); }, 8000);
      var resp = await fetch(API, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(corpo), signal: ctl.signal });
      clearTimeout(t);
      if (resp.ok) {
        var dados = await resp.json();
        if (dados && dados.uuid) destino = CHECKOUT + encodeURIComponent(dados.uuid);
      }
    } catch (e) { /* sem simulação do parceiro: segue sem pré-preenchimento */ }
    // dá tempo de o evento do Umami sair antes de trocar de página
    await new Promise(function (r) { setTimeout(r, 350); });
    window.location.href = destino;
    setTimeout(function () { btn.disabled = false; btn.textContent = rotulo; }, 3000);
  }

  function iniciar() {
    $('btn-modo-valor').addEventListener('click', function () { estado.modo = 'valor'; desenhar(); });
    $('btn-modo-limite').addEventListener('click', function () { estado.modo = 'limite'; desenhar(); });
    $('range-valor').addEventListener('input', function (e) { definirCampo(Number(e.target.value)); interagiu(); desenhar(); });
    $('campo-valor').addEventListener('input', function (e) {
      var v = Number(e.target.value);
      if (v > 0) { definirCampo(v); interagiu(); desenhar(); }
    });
    $('campo-valor').addEventListener('blur', function () { desenhar(); });
    $('range-parcelas').addEventListener('input', function (e) { estado.parcelas = Number(e.target.value); interagiu(); desenhar(); });
    $('cta-pix').addEventListener('click', abrirProposta);
    var pc = window.matchMedia && window.matchMedia('(pointer: fine) and (min-width: 900px)').matches;
    $('aviso-celular').classList.toggle('hidden', !pc);
    desenhar();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})();
