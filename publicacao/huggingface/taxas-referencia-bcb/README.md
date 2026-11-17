---
license: odbl
language:
- pt
pretty_name: "Taxas médias de crédito PF do Banco Central"
size_categories:
- n<1K
configs:
- config_name: default
  data_files: taxas-referencia-bcb.csv
tags:
- "finance"
- "brazil"
- "banking"
- "interest rates"
- "central bank"
---

# Taxas médias de juros do Banco Central: cheque especial, crédito pessoal não consignado e cartão rotativo

Taxa média de juros das novas operações de crédito com recursos livres, pessoas físicas, ponderada pelo valor das concessões, em % ao ano, série mensal, para cheque especial (SGS 20741), crédito pessoal não consignado (SGS 20742) e cartão de crédito rotativo (SGS 22022). Inclui a taxa ao mês equivalente, calculada por juros compostos.

## Colunas
- `codigo_serie` (integer): Código da série no SGS do Banco Central
- `modalidade` (string): Modalidade de crédito
- `mes_referencia` (string): Mês de referência (AAAA-MM)
- `taxa_aa_pct` (number): Taxa média de juros, % ao ano (dado do Banco Central)
- `taxa_am_equivalente_pct` (number): Taxa ao mês equivalente, % (cálculo da Datalab Global)
- `fonte_url` (string): Endereço da série no SGS (JSON)

## Licença e fonte
Contém informações do Banco Central do Brasil, disponibilizadas por ele sob a licença ODbL 1.0 (https://opendatacommons.org/licenses/odbl/1-0/). Esta base derivada também é licenciada sob ODbL 1.0: você pode copiar, distribuir e adaptar, citando a fonte e mantendo a mesma licença.

Fonte: Banco Central do Brasil — SGS (dados abertos, ODbL) (https://dadosabertos.bcb.gov.br/).
