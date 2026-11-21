/* GERADO por gerador_emprestimo.py a partir de dados/emprestimo-cartao-tabela-esperada.json. Não edite à mão.
   Mesma conta de calculo.py (os testes comparam os dois). */
(function (root) {
  'use strict';
  var T = {"cet": {"10": {"annual": 190.26, "monthly": 8.87}, "11": {"annual": 167.14, "monthly": 8.12}, "12": {"annual": 148.97, "monthly": 7.49}, "2": {"annual": 3621.21, "monthly": 34.64}, "3": {"annual": 1482.58, "monthly": 25.39}, "4": {"annual": 837.48, "monthly": 20.04}, "5": {"annual": 558.16, "monthly": 16.55}, "6": {"annual": 409.99, "monthly": 14.1}, "7": {"annual": 320.64, "monthly": 12.29}, "8": {"annual": 261.83, "monthly": 10.89}, "9": {"annual": 220.59, "monthly": 9.78}}, "fator_base": 0.5479, "fator_por_parcela": 0.003, "iof_fixo": 0.0038, "iof_por_parcela": 0.00246, "table_name": "TABELA 10", "table_uuid": "0IHX41YEUXXD", "valor_max": 5000};
  var VALOR_MIN = 300;
  var VALOR_MAX = T.valor_max;
  // Taxas médias de juros do Banco Central (referência, não oferta): aa = ao ano, am = ao mês equivalente (juros compostos).
  var REF = [{"aa": 110.94, "am": 6.4175, "chave": "pessoal-nao-consignado", "mes": "setembro de 2026", "nome": "Crédito pessoal não consignado"}, {"aa": 139.02, "am": 7.5316, "chave": "cheque-especial", "mes": "setembro de 2026", "nome": "Cheque especial"}, {"aa": 451.71, "am": 15.2947, "chave": "cartao-rotativo", "mes": "setembro de 2026", "nome": "Cartão de crédito rotativo"}];

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
