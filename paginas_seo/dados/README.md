# Dados abertos: empréstimo pessoal com crédito do cartão (Datalab Global)

Gerado automaticamente pelo simulador em https://emprestimo.datalabglobal.com. Cada conjunto tem a licença que a sua fonte permite.


## Empréstimo pessoal com crédito do cartão: Tabela 10 do parceiro (parcela, IOF, juros e CET)

Condições do empréstimo pessoal com crédito do cartão (o limite do cartão de crédito é a fonte do dinheiro, entregue por Pix) segundo a Tabela 10 do parceiro (correspondente bancário), de 2 a 12 parcelas, para cada R$ 1.000 recebidos: fator total, parcela, total na fatura, IOF, juros ao mês, juros equivalentes ao ano e CET ao ano. Valor recebido de R$ 300 a R$ 5.000. Os números são conferidos toda semana contra a API do próprio parceiro.

- Arquivos: `emprestimo-cartao-tabela-10.csv`, `emprestimo-cartao-tabela-10.json`, `datapackage-emprestimo-cartao-tabela-10.json`
- Licença CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/deed.pt-br): você pode copiar, distribuir e adaptar, citando Datalab Global (https://emprestimo.datalabglobal.com/dados-abertos).
- Como citar: Datalab Global (https://emprestimo.datalabglobal.com/dados-abertos).
- Linhas: 11

Colunas:

- `parcelas` (integer): Número de parcelas na fatura (2 a 12)
- `juros_am_pct` (number): Juros ao mês, % (tabelado pelo parceiro)
- `juros_aa_equivalente_pct` (number): Juros ao ano equivalentes (juros compostos sobre a taxa mensal), %
- `cet_aa_pct` (number): Custo efetivo total ao ano, % (tabelado pelo parceiro)
- `fator_total` (number): Fator da Tabela 10: 0,5479 + 0,003 x parcelas. Total na fatura = valor recebido x (1 + fator)
- `parcela_por_r1000` (number): Valor de cada parcela, em R$, para receber R$ 1.000
- `total_por_r1000` (number): Total na fatura, em R$, para receber R$ 1.000
- `iof_por_r1000` (number): IOF (já incluso no total), em R$, para receber R$ 1.000

## Taxas médias de juros do Banco Central: cheque especial, crédito pessoal não consignado e cartão rotativo

Taxa média de juros das novas operações de crédito com recursos livres, pessoas físicas, ponderada pelo valor das concessões, em % ao ano, série mensal, para cheque especial (SGS 20741), crédito pessoal não consignado (SGS 20742) e cartão de crédito rotativo (SGS 22022). Inclui a taxa ao mês equivalente, calculada por juros compostos.

- Arquivos: `taxas-referencia-bcb.csv`, `taxas-referencia-bcb.json`, `datapackage-taxas-referencia-bcb.json`
- Contém informações do Banco Central do Brasil, disponibilizadas por ele sob a licença ODbL 1.0 (https://opendatacommons.org/licenses/odbl/1-0/). Esta base derivada também é licenciada sob ODbL 1.0: você pode copiar, distribuir e adaptar, citando a fonte e mantendo a mesma licença.
- Como citar: Datalab Global (https://emprestimo.datalabglobal.com/dados-abertos).
- Linhas: 69

Colunas:

- `codigo_serie` (integer): Código da série no SGS do Banco Central
- `modalidade` (string): Modalidade de crédito
- `mes_referencia` (string): Mês de referência (AAAA-MM)
- `taxa_aa_pct` (number): Taxa média de juros, % ao ano (dado do Banco Central)
- `taxa_am_equivalente_pct` (number): Taxa ao mês equivalente, % (cálculo da Datalab Global)
- `fonte_url` (string): Endereço da série no SGS (JSON)

Limites: as taxas do Banco Central são médias de mercado, não ofertas. A Tabela 10 é do parceiro e pode mudar; a conferência é semanal.
