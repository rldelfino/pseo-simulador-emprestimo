---
license: cc-by-4.0
language:
- pt
pretty_name: Pix no cartão de crédito: parcela, IOF, juros e CET (Brasil, Tabela 10)
size_categories:
- n<1K
tags:
- finance
- brazil
- credit card
- interest rates
- installments
---

# Pix no cartão de crédito: Tabela 10 do parceiro (parcela, IOF, juros e CET)

Condições do Pix no cartão de crédito segundo a Tabela 10 do parceiro (correspondente bancário), de 2 a 12 parcelas, para cada R$ 1.000 recebidos por Pix: fator total, parcela, total na fatura, IOF, juros ao mês, juros equivalentes ao ano e CET ao ano. Valor do Pix de R$ 300 a R$ 5.000. Os números são conferidos toda semana contra a API do próprio parceiro.

## Colunas
- `parcelas` (integer): Número de parcelas na fatura (2 a 12)
- `juros_am_pct` (number): Juros ao mês, % (tabelado pelo parceiro)
- `juros_aa_equivalente_pct` (number): Juros ao ano equivalentes (juros compostos sobre a taxa mensal), %
- `cet_aa_pct` (number): Custo efetivo total ao ano, % (tabelado pelo parceiro)
- `fator_total` (number): Fator da Tabela 10: 0,5479 + 0,003 x parcelas. Total na fatura = valor no Pix x (1 + fator)
- `parcela_por_r1000` (number): Valor de cada parcela, em R$, para receber R$ 1.000
- `total_por_r1000` (number): Total na fatura, em R$, para receber R$ 1.000
- `iof_por_r1000` (number): IOF (já incluso no total), em R$, para receber R$ 1.000

## Licença e fonte
Licença CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/deed.pt-br): você pode copiar, distribuir e adaptar, citando Datalab Global (https://emprestimo.datalabglobal.com/dados-abertos).

Fonte: Parceiro do Pix no cartão (correspondente bancário) — Tabela 10, conferida pela API de simulação (https://emprestimo.datalabglobal.com/metodologia).
