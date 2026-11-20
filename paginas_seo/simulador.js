/* Interface do simulador do empréstimo pessoal com crédito do cartão. Só textContent e atributos SVG (nada de innerHTML).
   Depende de calculo.js (window.DatalabEmprestimo). Sem cookies e sem dado pessoal: só valor e prazo vão para a simulação do parceiro e para o Umami.
   Eventos do Umami: usou-simulador-emprestimo, abriu-confirmacao, cta-parceiro, cta-parceiro-sem-preenchimento, copiou-link, usou-proposta-propria. */
(function () {
  'use strict';
  var P = window.DatalabEmprestimo;
  if (!P) return;

  var API = 'https://api.triagem.digital/proposals/simulator';
  var CHECKOUT = 'https://checkoutonline.digital/?l=' + P.tableUUID + '&u=ucHWD4k1tat4&lp=gyroo&wl=gyroo&s=';
  var LIMITE_MIN = 300;
  var LIMITE_MAX = 8000;
  var SVG = 'http://www.w3.org/2000/svg';
  var CHAVE_SESSAO = 'emp-sim';
  var CIRC = 289.03;

  var estado = { modo: 'valor', valor: 1000, limite: 2000, parcelas: 12, prop: '' };
  var usou = false;
  var usouProp = false;
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

  function valorCampo() { return estado.modo === 'valor' ? estado.valor : estado.limite; }

  function limiteNecessario(parcelas) {
    var T = P.tabela;
    return Math.ceil(P.VALOR_MIN * (1 + T.fator_base + T.fator_por_parcela * parcelas));
  }

  function limitesDoCampo() {
    return estado.modo === 'valor' ? [P.VALOR_MIN, P.VALOR_MAX] : [LIMITE_MIN, LIMITE_MAX];
  }

  // O preenchimento colorido do controle deslizante usa data-p (0 a 100): o CSS não permite style no HTML, então a variável vem de uma regra por valor.
  function marcarSlider(el, min, max) {
    var p = max > min ? Math.round(((Number(el.value) - min) / (max - min)) * 100) : 0;
    el.setAttribute('data-p', String(clamp(p, 0, 100)));
  }

  function desenharRosca(receber, total) {
    var parte = total > 0 ? (receber / total) * CIRC : 0;
    $('rosca-valor').setAttribute('stroke-dasharray', parte.toFixed(2) + ' ' + (CIRC - parte).toFixed(2));
    var custo = total > 0 ? Math.round(((total - receber) / total) * 100) : 0;
    $('rosca-pct').textContent = custo + '%';
    $('donut').setAttribute('aria-label', 'Do total na fatura, ' + custo + '% é juros e IOF');
    $('leg-valor').textContent = P.brl(receber);
    $('leg-custo').textContent = P.brl(total - receber);
  }

  function desenharBarras(receber) {
    var alvo = $('barras');
    limpar(alvo);
    var linhas = [];
    var maior = 0;
    for (var n = 2; n <= 12; n++) {
      var c = P.simular('valor', receber, 0, n);
      linhas.push({ n: n, extra: c.total - receber, parcela: c.parcela });
      if (c.total - receber > maior) maior = c.total - receber;
    }
    linhas.forEach(function (l) {
      var b = document.createElement('button');
      b.type = 'button';
      var ativa = l.n === estado.parcelas;
      b.className = 'pz';
      b.setAttribute('aria-label', l.n + ' parcelas de ' + P.brl(l.parcela) + ', paga ' + P.brl(l.extra) + ' a mais');
      b.setAttribute('aria-pressed', String(ativa));
      var rot = document.createElement('span');
      rot.className = 'pzn num';
      rot.textContent = l.n + 'x';
      var barra = svg('svg', { viewBox: '0 0 100 8', preserveAspectRatio: 'none', 'class': 'pzb', 'aria-hidden': 'true' });
      barra.appendChild(svg('rect', { width: '100', height: '8', rx: '4', fill: 'rgba(255,255,255,.08)' }));
      barra.appendChild(svg('rect', { width: (maior > 0 ? (l.extra / maior) * 100 : 0).toFixed(1), height: '8', rx: '4', fill: ativa ? '#c4b5fd' : '#8b5cf6' }));
      var val = document.createElement('span');
      val.className = 'pv num';
      val.textContent = P.brl(l.extra);
      var parc = document.createElement('span');
      parc.className = 'pp num';
      parc.textContent = 'parcela ' + P.brl(l.parcela);
      b.appendChild(rot); b.appendChild(barra); b.appendChild(val); b.appendChild(parc);
      b.addEventListener('click', function () { estado.parcelas = l.n; interagiu(); desenhar(); });
      alvo.appendChild(b);
    });
    var minimo = linhas[0];
    var maximo = linhas[linhas.length - 1];
    $('txt-barras').textContent = 'Para receber ' + P.brl(receber) + ', você paga ' + P.brl(minimo.extra) + ' a mais em 2x e ' + P.brl(maximo.extra) +
      ' a mais em 12x: só ' + P.brl(maximo.extra - minimo.extra) + ' de diferença entre o prazo mais curto e o mais longo.';
  }

  function desenharTabela(receber) {
    $('cap-prazos').textContent = 'Para receber ' + P.brl(receber) + ' na conta. Fonte: Tabela 10 do parceiro.';
    var corpo = $('corpo-prazos');
    limpar(corpo);
    var rotulos = ['Prazo', 'Parcela', 'Total na fatura', 'Custo a mais', 'Juros ao mês', 'CET ao ano'];
    for (var n = 2; n <= 12; n++) {
      var c = P.simular('valor', receber, 0, n);
      var ativa = n === estado.parcelas;
      var tr = document.createElement('tr');
      if (ativa) { tr.setAttribute('aria-current', 'true'); tr.className = 'atual'; }
      [n + 'x', P.brl(c.parcela), P.brl(c.total), P.brl(c.total - receber), P.pct(c.jurosMes), P.pct(c.cetAno)].forEach(function (txt, i) {
        var td = document.createElement('td');
        td.className = 'num';
        td.setAttribute('data-l', rotulos[i]);
        td.textContent = txt;
        tr.appendChild(td);
      });
      corpo.appendChild(tr);
    }
  }

  // Compara os juros ao mês deste empréstimo com as médias do Banco Central (juros com juros, nunca CET com juros). Sem dado, o bloco some.
  function desenharReferencia(r, escondido) {
    var refs = P.referencias || [];
    var bloco = $('referencia');
    if (!refs.length || escondido) { bloco.hidden = true; return; }
    bloco.hidden = false;
    var lista = $('ref-lista');
    limpar(lista);
    function linha(nome, valor, destaque) {
      var li = document.createElement('li');
      if (destaque) li.className = 'us';
      var a = document.createElement('span');
      a.textContent = nome;
      var b = document.createElement('span');
      b.className = 'num';
      b.textContent = valor;
      li.appendChild(a); li.appendChild(b);
      lista.appendChild(li);
    }
    linha('Empréstimo com crédito do cartão em ' + estado.parcelas + 'x', P.pct(r.jurosMes) + ' ao mês', true);
    var meses = [];
    refs.forEach(function (x) {
      linha(x.nome + ' (média)', P.pct(x.am) + ' ao mês', false);
      if (meses.indexOf(x.mes) < 0) meses.push(x.mes);
    });
    var menores = refs.filter(function (x) { return x.am < r.jurosMes * 0.97; });
    var texto;
    if (menores.length === refs.length) {
      texto = 'Em média, as ' + refs.length + ' modalidades acima têm juros menores que este empréstimo em ' + estado.parcelas + 'x. Peça o CET dessas alternativas antes de decidir.';
    } else if (menores.length === 0) {
      texto = 'Nenhuma das médias acima tem juros claramente menores que este empréstimo em ' + estado.parcelas + 'x.';
    } else {
      var nomes = menores.map(function (x) { return x.nome.toLowerCase(); }).join(' e ');
      texto = 'Em média, ' + nomes + (menores.length > 1 ? ' têm' : ' tem') + ' juros menores que este empréstimo em ' + estado.parcelas + 'x. Peça o CET dessas alternativas antes de decidir.';
    }
    $('ref-veredito').textContent = texto;
    $('ref-nota').textContent = 'Média das novas operações de crédito de pessoas físicas (Banco Central, ' + meses.join(' e ') +
      '). É taxa de juros, não é CET, e não é oferta: a sua pode ser maior ou menor.';
  }

  // "Já tem uma proposta?": a taxa de juros ao mês que a parcela informada cobra, para o mesmo valor e prazo, ao lado da Tabela 10.
  var MSG_PROP_PADRAO = 'Usa o valor que você recebe e o número de parcelas escolhidos acima. Informe a parcela que aparece na proposta e veja quanto ela cobra de juros ao mês.';
  function desenharProposta(r, abaixo) {
    var msg = $('msg-prop');
    var v = lerNumero(estado.prop);
    msg.classList.remove('warn');
    if (!(v > 0) || abaixo) { msg.textContent = MSG_PROP_PADRAO; return; }
    var taxa = P.taxaImplicita(r.receber, v, estado.parcelas);
    if (taxa === null) {
      msg.textContent = 'Com ' + estado.parcelas + ' parcelas de ' + P.brl(v) + ' você pagaria menos do que recebe (' + P.brl(r.receber) + '). Confira a parcela e o valor.';
      msg.classList.add('warn');
      return;
    }
    if (taxa > 500) {
      msg.textContent = 'Essa parcela dá juros acima de 500% ao mês. Confira os números da proposta.';
      msg.classList.add('warn');
      return;
    }
    var totalProp = v * estado.parcelas;
    var dif = totalProp - r.total;
    var comp = Math.abs(dif) < 1 ? 'praticamente o mesmo total' : (dif > 0 ? P.brl(dif) + ' a mais no total' : P.brl(-dif) + ' a menos no total');
    // as duas taxas saem da mesma conta (parcelas iguais, sem tarifas): a taxa que o parceiro tabela (r.jurosMes) usa outro método e fica um pouco abaixo
    var taxaTabela = P.taxaImplicita(r.receber, r.parcela, estado.parcelas);
    msg.textContent = 'Pela mesma conta, a proposta equivale a ' + P.pct(taxa) + ' ao mês (' + estado.parcelas + ' x ' + P.brl(v) + ' = ' + P.brl(totalProp) + ') e a Tabela 10, em ' +
      estado.parcelas + 'x, a ' + P.pct(taxaTabela) + ' ao mês (total ' + P.brl(r.total) + '; o parceiro informa ' + P.pct(r.jurosMes) + ' por outro método de cálculo). A proposta tem ' + comp +
      '. Se a parcela dela inclui tarifas ou seguros, a taxa de juros é menor; peça o CET por escrito.';
    if (!usouProp) { usouProp = true; evento('usou-proposta-propria', { prazo: estado.parcelas }); }
  }

  // Endereço compartilhável: modo, valor (ou limite), parcelas e a parcela da proposta. Sem dado pessoal. O canonical da página continua sendo a home.
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
      if (v > 0) estado.valor = clamp(v, P.VALOR_MIN, P.VALOR_MAX);
      var tl = q.get('limite') || '';
      var l = soNumero.test(tl) ? lerNumero(tl) : 0;
      if (l > 0) estado.limite = clamp(l, LIMITE_MIN, LIMITE_MAX);
      var tp = q.get('prop') || '';
      if (soNumero.test(tp) && lerNumero(tp) > 0) estado.prop = tp;
    } catch (e) { /* endereço estranho: usa os valores padrão */ }
  }

  function enderecoDaSimulacao(comHash) {
    var q = new URLSearchParams();
    q.set('modo', estado.modo);
    q.set(estado.modo, String(Math.round(valorCampo() * 100) / 100));
    q.set('parcelas', String(estado.parcelas));
    var v = lerNumero(estado.prop);
    if (v > 0) q.set('prop', String(Math.round(v * 100) / 100));
    return window.location.origin + window.location.pathname + '?' + q.toString() + (comHash === false ? '' : '#simulador');
  }

  // Guarda a última simulação só nesta aba (sessionStorage, sem cookie) para o botão "Voltar à simulação" das páginas internas.
  function guardarSimulacao() {
    try { window.sessionStorage.setItem(CHAVE_SESSAO, '?' + enderecoDaSimulacao(false).split('?')[1]); } catch (e) { /* sem armazenamento: o botão leva ao simulador */ }
  }

  function atualizarEndereco() {
    clearTimeout(timerUrl);
    // espera a pessoa parar de mexer: o navegador limita as trocas de endereço por segundo
    timerUrl = setTimeout(function () {
      try { window.history.replaceState(null, '', enderecoDaSimulacao()); } catch (e) { /* sem histórico: o botão de copiar continua valendo */ }
      guardarSimulacao();
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
        t.className = 'sr';
        document.body.appendChild(t);
        t.select();
        ok = document.execCommand('copy');
        document.body.removeChild(t);
      } catch (e) { ok = false; }
    }
    var msg = $('msg-copiado');
    msg.textContent = ok ? 'Link copiado. Quem abrir vê esta mesma simulação.' : 'Não deu para copiar sozinho. O link já está na barra de endereço do navegador.';
    clearTimeout(timerCopiado);
    timerCopiado = setTimeout(function () { msg.textContent = ''; }, 4000);
    evento('copiou-link', { valor: valorCampo(), prazo: estado.parcelas, modo: estado.modo });
  }

  function desenhar() {
    var r = P.simular(estado.modo, estado.valor, estado.limite, estado.parcelas);
    var lim = limitesDoCampo();
    var campo = valorCampo();
    var abaixo = estado.modo === 'limite' && r.receber < P.VALOR_MIN;
    var ehValor = estado.modo === 'valor';

    $('rotulo-valor').firstChild.textContent = ehValor ? 'Valor que você quer receber ' : 'Limite disponível no cartão ';
    $('sub-valor').textContent = ehValor ? 'cai na conta, por Pix' : 'o quanto você pode usar';
    $('range-valor').min = lim[0]; $('range-valor').max = lim[1];
    $('range-valor').value = clamp(campo, lim[0], lim[1]);
    $('range-valor').setAttribute('aria-valuetext', P.brl(Number($('range-valor').value)));
    marcarSlider($('range-valor'), lim[0], lim[1]);
    if (document.activeElement !== $('campo-valor')) $('campo-valor').value = BRL_NUM.format(campo);
    $('min-valor').textContent = P.brl(lim[0]);
    $('max-valor').textContent = P.brl(lim[1]);
    $('range-parcelas').value = estado.parcelas;
    $('range-parcelas').setAttribute('aria-valuetext', estado.parcelas + ' parcelas');
    marcarSlider($('range-parcelas'), 2, 12);
    $('txt-parcelas').textContent = estado.parcelas + 'x';
    if (document.activeElement !== $('campo-prop')) $('campo-prop').value = estado.prop;

    $('btn-modo-valor').setAttribute('aria-selected', String(ehValor));
    $('btn-modo-limite').setAttribute('aria-selected', String(!ehValor));
    $('btn-modo-valor').tabIndex = ehValor ? 0 : -1;
    $('btn-modo-limite').tabIndex = ehValor ? -1 : 0;
    $('painel-simulacao').setAttribute('aria-labelledby', ehValor ? 'btn-modo-valor' : 'btn-modo-limite');

    $('r-parcela').textContent = P.brl(r.parcela);
    $('r-sub').textContent = estado.parcelas + ' parcelas · você recebe ' + P.brl(r.receber);
    $('r-total').textContent = P.brl(r.total);
    $('r-receber').textContent = P.brl(r.receber);
    $('nota-limite').textContent = 'O total na fatura (' + P.brl(r.total) + ') fica comprometido no limite até as parcelas serem pagas.';
    $('r-iof').textContent = P.brl(r.iof);
    $('r-juros').textContent = P.pct(r.jurosMes);
    $('r-cet').textContent = P.pct(r.cetAno);
    $('k-real').textContent = P.brl(r.total / r.receber);
    $('r-resumo').textContent = 'Você recebe ' + P.brl(r.receber) + ' e paga ' + P.brl(r.total) + ' na fatura: ' + P.brl(r.total - r.receber) + ' a mais, com juros e IOF.';
    $('aviso-minimo').hidden = !abaixo;
    if (abaixo) {
      $('aviso-minimo').textContent = 'Com esse limite, o valor ficaria abaixo do mínimo de ' + P.brl(P.VALOR_MIN) + '. Em ' + estado.parcelas +
        'x, você precisa de um limite de pelo menos ' + P.brl(limiteNecessario(estado.parcelas)) + ', ou diminua as parcelas.';
    }
    $('btn-cta').disabled = abaixo;
    $('resumo-parcela').textContent = abaixo ? 'Limite abaixo do mínimo' : estado.parcelas + 'x de ' + P.brl(r.parcela);
    $('resumo-total').textContent = abaixo ? 'Aumente o limite ou diminua as parcelas' : 'Total na fatura ' + P.brl(r.total);
    $('dlg-resumo').textContent = 'Você recebe ' + P.brl(r.receber) + ' por Pix e paga ' + P.brl(r.total) + ' na fatura (' + estado.parcelas + 'x de ' + P.brl(r.parcela) +
      '): ' + P.brl(r.total - r.receber) + ' a mais, com juros e IOF.';

    desenharRosca(r.receber, r.total);
    desenharBarras(r.receber);
    desenharReferencia(r, abaixo);
    desenharTabela(r.receber);
    desenharProposta(r, abaixo);
    desenhos += 1;
    if (desenhos > 1) atualizarEndereco();  // o primeiro desenho é o da carga da página
  }

  function interagiu() {
    if (usou) return;
    usou = true;
    evento('usou-simulador-emprestimo', { valor: valorCampo(), prazo: estado.parcelas });
  }

  function definirCampo(v) {
    var lim = limitesDoCampo();
    if (estado.modo === 'valor') estado.valor = clamp(v, lim[0], lim[1]); else estado.limite = clamp(v, lim[0], lim[1]);
  }

  // Segundo passo: com a pessoa já ciente (tela de confirmação), pede ao parceiro uma simulação com o valor e o prazo e abre a proposta pré-preenchida.
  async function irParaParceiro() {
    var btn = $('btn-parceiro');
    if (btn.disabled) return;
    btn.disabled = true;
    var rotulo = btn.textContent;
    $('aviso-proposta').hidden = true;
    btn.textContent = 'Abrindo a proposta...';
    evento('cta-parceiro', { valor: valorCampo(), prazo: estado.parcelas, modo: estado.modo });
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
      var valorTxt = estado.modo === 'valor' ? P.brl(estado.valor) + ' na conta' : 'limite de ' + P.brl(estado.limite);
      $('txt-aviso-proposta').textContent = 'Não conseguimos pré-preencher a proposta agora. Você pode tentar de novo ou continuar no parceiro e informar lá ' +
        valorTxt + ' em ' + estado.parcelas + 'x. ';
      $('link-parceiro').href = CHECKOUT;
      $('aviso-proposta').hidden = false;
      evento('cta-parceiro-sem-preenchimento', { prazo: estado.parcelas, modo: estado.modo });
      btn.disabled = false;
      btn.textContent = rotulo;
      return;
    }
    var destino = CHECKOUT + encodeURIComponent(uuid);
    // dá tempo de o evento do Umami sair antes de trocar de página
    await new Promise(function (resolve) { setTimeout(resolve, 350); });
    window.location.href = destino;
    setTimeout(function () { btn.disabled = false; btn.textContent = rotulo; }, 3000);
  }

  // Barra fixa no celular: enquanto a pessoa mexe nos controles e o resultado está fora da tela, mostra parcela e total.
  function iniciarBarraResumo() {
    var barra = $('barra-resumo');
    if (!barra || !('IntersectionObserver' in window)) return;
    var vendo = { simulador: false, resultado: false };
    function atualizar() { barra.hidden = !(vendo.simulador && !vendo.resultado); }
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
      e.target.value = BRL_NUM.format(valorCampo());  // mostra o valor já ajustado à faixa
    });
    $('campo-valor').addEventListener('keydown', function (e) { if (e.key === 'Enter') e.target.blur(); });
    $('range-parcelas').addEventListener('input', function (e) { estado.parcelas = Number(e.target.value); interagiu(); desenhar(); });
    $('campo-prop').addEventListener('input', function (e) { estado.prop = e.target.value.replace(/[^\d.,]/g, '').slice(0, 12); desenhar(); });
    $('campo-prop').addEventListener('blur', function () { desenhar(); });
    $('campo-prop').addEventListener('keydown', function (e) { if (e.key === 'Enter') e.target.blur(); });
    $('btn-copiar').addEventListener('click', copiarLink);
    iniciarBarraResumo();
    var pc = window.matchMedia && window.matchMedia('(pointer: fine) and (min-width: 900px)').matches;
    $('aviso-celular').hidden = !pc;

    var dlg = $('dlg-confirma');
    function devolverFoco() { try { $('btn-cta').focus({ preventScroll: true }); } catch (e) { /* ignora */ } }
    function fechar() { if (typeof dlg.close === 'function') dlg.close(); else { dlg.removeAttribute('open'); devolverFoco(); } }
    $('btn-cta').addEventListener('click', function () {
      if ($('btn-cta').disabled) return;
      evento('abriu-confirmacao', { valor: valorCampo(), prazo: estado.parcelas, modo: estado.modo });
      $('aviso-proposta').hidden = true;
      if (typeof dlg.showModal === 'function') dlg.showModal(); else dlg.setAttribute('open', '');
    });
    dlg.addEventListener('close', devolverFoco);
    $('btn-voltar').addEventListener('click', fechar);
    $('btn-parceiro').addEventListener('click', irParaParceiro);
    // Só o clique fora da caixa fecha (o preenchimento interno do diálogo também é o próprio elemento: conferimos pelas coordenadas).
    dlg.addEventListener('click', function (e) {
      if (e.target !== dlg) return;
      var r = dlg.getBoundingClientRect();
      var fora = e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom;
      if (fora) fechar();
    });
    // Voltar do parceiro com o botão do navegador: a página pode vir do cache com o botão travado em "Abrindo...".
    window.addEventListener('pageshow', function (e) {
      if (!e.persisted) return;
      $('btn-parceiro').disabled = false;
      $('btn-parceiro').textContent = 'Continuar para o parceiro →';
      fechar();
    });
    desenhar();
    guardarSimulacao();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})();
