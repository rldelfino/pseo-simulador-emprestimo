/* Interface do simulador. Só textContent (nada de innerHTML). Depende de calculo.js (window.DatalabPix).
   Sem cookies e sem dado pessoal: só valor e prazo vão para a simulação do parceiro e para o Umami. */
(function () {
  'use strict';
  var P = window.DatalabPix;
  if (!P) return;

  var API = 'https://api.triagem.digital/proposals/simulator';
  var CHECKOUT = 'https://checkoutonline.digital/?l=' + P.tableUUID + '&u=ucHWD4k1tat4&lp=gyroo&wl=gyroo&s=';
  var LIMITE_MIN = 500;
  var LIMITE_MAX = 8000;

  var estado = { modo: 'valor', valor: 1000, limite: 2000, parcelas: 12 };
  var usou = false;

  function $(id) { return document.getElementById(id); }
  function clamp(v, a, b) { return Math.min(b, Math.max(a, v)); }
  function evento(nome, dados) {
    try { if (window.umami && window.umami.track) window.umami.track(nome, dados); } catch (e) { /* medição nunca quebra o simulador */ }
  }

  function limitesDoCampo() {
    return estado.modo === 'valor' ? [P.PIX_MIN, P.PIX_MAX] : [LIMITE_MIN, LIMITE_MAX];
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
    $('r-juros').textContent = P.pct(r.jurosMes) + ' ao mês';
    $('r-cet').textContent = P.pct(r.cetAno) + ' ao ano';
    $('r-custo-texto').textContent = 'Você recebe ' + P.brl(r.pix) + ' e paga ' + P.brl(r.total) +
      ' na fatura: ' + P.brl(r.total - r.pix) + ' a mais, com juros e IOF.';
    $('aviso-minimo').classList.toggle('hidden', !abaixo);
    $('cta-pix').disabled = abaixo;

    var comp = $('comparativo');
    while (comp.firstChild) comp.removeChild(comp.firstChild);
    var menor = null;
    [3, 6, 9, 12].forEach(function (n) {
      var c = P.simular('valor', r.pix, 0, n);
      if (!menor || c.total < menor.total) menor = { n: n, total: c.total };
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'comp-op rounded-xl border p-3 text-left text-sm ' +
        (n === estado.parcelas ? 'border-violet-400 bg-violet-400/10 text-violet-100' : 'border-white/10 bg-slate-950/50 text-slate-300');
      var t1 = document.createElement('div'); t1.className = 'font-bold text-white'; t1.textContent = n + 'x de ' + P.brl(c.parcela);
      var t2 = document.createElement('div'); t2.className = 'mt-1 text-xs'; t2.textContent = 'Total ' + P.brl(c.total);
      b.appendChild(t1); b.appendChild(t2);
      b.addEventListener('click', function () { estado.parcelas = n; interagiu(); desenhar(); });
      comp.appendChild(b);
    });
    $('txt-comparativo').textContent = 'Mais parcelas deixam a prestação menor, mas o total na fatura cresce. Para receber ' +
      P.brl(r.pix) + ', o menor total entre essas opções é em ' + menor.n + 'x (' + P.brl(menor.total) + ').';
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
