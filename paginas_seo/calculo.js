/* GERADO por gerador_emprestimo.py a partir de dados/pix-tabela-esperada.json. Não edite à mão.
   Mesma conta de calculo.py (os testes comparam os dois). */
(function (root) {
  'use strict';
  var T = {"cet": {"10": {"annual": 190.26, "monthly": 8.87}, "11": {"annual": 167.14, "monthly": 8.12}, "12": {"annual": 148.97, "monthly": 7.49}, "2": {"annual": 3621.21, "monthly": 34.64}, "3": {"annual": 1482.58, "monthly": 25.39}, "4": {"annual": 837.48, "monthly": 20.04}, "5": {"annual": 558.16, "monthly": 16.55}, "6": {"annual": 409.99, "monthly": 14.1}, "7": {"annual": 320.64, "monthly": 12.29}, "8": {"annual": 261.83, "monthly": 10.89}, "9": {"annual": 220.59, "monthly": 9.78}}, "fator_base": 0.5479, "fator_por_parcela": 0.003, "iof_fixo": 0.0038, "iof_por_parcela": 0.00246, "pix_max": 5000, "table_name": "TABELA 10", "table_uuid": "0IHX41YEUXXD"};
  var PIX_MIN = 300;
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
