# Simulador de empréstimo ("Pix no cartão") — Datalab Global

Idioma: português do Brasil. Estilo: curto, sem jargão, números reais, dizer o que NÃO foi verificado.

## Regras fixas
- **Graphify primeiro, sempre, sem o dono pedir.** Antes de ler arquivo/grep: `graphify update .` e `graphify query "..."`. Se pular, avisar na hora.
- Sem gastar dinheiro. Sem postar nem mandar mensagem a pessoas. Cadastro em diretórios/dados abertos é permitido.
- LGPD: nada de CPF/telefone em log, teste ou arquivo. Fluxo do parceiro só com dados de teste do dono.
- Medição: Umami (sem cookies), Website ID `ba3c0b88-59e8-47dd-866d-0b05e5e7dae9`. Dados abertos CC BY 4.0. Sem AdSense.
- Nada de "Banco A × Banco B" nem ranking que induza a pedir um banco.
- Sem segredo em arquivo/GitHub. Sem identificar modelo de IA em commits/PRs.
- Merge só com `pytest` saindo 0 (não usar `pytest | tail`). Python 3.10 (sem f-string aninhado).
- Máximo ~30 páginas indexáveis, cada uma com conteúdo próprio. Sem grade de páginas quase iguais.

## Origem
`origem-hub/` é uma cópia (13/11/2026) do código do Pix no cartão que nasceu no harness
(`Documents/Datalab/harness/projects/datalab-global-hub`). O dono não mexe mais lá; a partir daqui a fonte é este projeto.
Referência: `origem-hub/pixcartao/components/calculo.ts` (conta), `proposta.ts` (envio), `tools/` (verificação semanal da Tabela 10).

## Fatos do produto
- API: `POST https://api.triagem.digital/proposals/simulator` `{parcels, tableUUID, desiredValue}`; Tabela 10, `tableUUID` `0IHX41YEUXXD`; teto R$ 5.000, 12 parcelas.
- Conta: fator = 0,5479 + 0,003·n; parcela = valor·(1+fator)/n; IOF = valor·(0,0038 + 0,00246·n).
- Checkout (Gyroo): no desktop mostra só QR Code (continua no celular); 6 passos; exige RG/CNH original em mãos.
