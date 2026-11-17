# Simulador de empréstimo ("Pix no cartão") — Datalab Global

Idioma: português do Brasil. Estilo: curto, sem jargão, números reais, dizer o que NÃO foi verificado.

## Regras fixas
- **Graphify primeiro, sempre, sem o dono pedir.** Antes de ler arquivo/grep: `graphify update .` e `graphify query "..."`. Se pular, avisar na hora.
- Sem gastar dinheiro. Sem postar nem mandar mensagem a pessoas. Cadastro em diretórios/dados abertos é permitido (dono dispensou o gov.br).
- LGPD: nada de CPF/telefone em log, teste ou arquivo. Fluxo do parceiro só com dados de teste do dono.
- Medição: Umami (sem cookies), Website ID `ba3c0b88-59e8-47dd-866d-0b05e5e7dae9` (COMPARTILHADO com imobiliário e veículos; no Umami filtrar por Hostname). Dados abertos CC BY 4.0. Sem AdSense.
- Nada de "Banco A × Banco B" nem ranking que induza a pedir um banco.
- Sem segredo em arquivo/GitHub (token do Kaggle = segredo `KAGGLE_API_TOKEN` do repo). Sem identificar modelo de IA em commits/PRs (só as linhas de atribuição que o sistema mandar).
- Merge só com `pytest` saindo 0 (não usar `pytest | tail`). Python 3.10 (sem f-string aninhado). Fluxo de alteração: branch → PR → merge (Windows mostra avisos LF/CRLF, normais).
- **Paleta: roxo/púrpura** (violet do Tailwind). Verde é do imobiliário e azul dos veículos: não usar aqui.
- Máximo ~30 páginas indexáveis, cada uma com conteúdo próprio. Sem grade de páginas quase iguais.
- Não baixar arquivo sem permissão do dono. Não mandar evento de teste ao Umami (contamina os números).

## Comandos
- Build: `python gerador_emprestimo.py` → `npm run build:css` → `python gerador_emprestimo.py` (o hash `?v=` do CSS/JS é calculado na geração).
- Testes: `python -m pytest -q` (94). Pacote de publicação: `python publicacao.py`.
- Fontes: `layout.py` (HTML), `conteudo.py` (textos, títulos ≤ 60 caracteres), `src/simulador.js`, `src/menu.js`, `gerador_emprestimo.py`. Saída: `paginas_seo/` (Cloudflare Pages, sem build). `gh` portátil: `C:\Users\rldel\tools\gh\app\bin`.
- Robô semanal `.github/workflows/atualiza_taxas.yml` (seg 08:00 UTC): taxas BCB, rebuild, IndexNow e, por último, Kaggle (Python 3.12, `continue-on-error`).

## Origem
`origem-hub/` é cópia (13/11/2026) do código que nasceu no harness (`Documents/Datalab/harness/projects/datalab-global-hub`); o dono não mexe mais lá. Referência: `origem-hub/pixcartao/components/calculo.ts`, `proposta.ts`, `tools/`.

## Fatos do produto
- API: `POST https://api.triagem.digital/proposals/simulator` `{parcels, tableUUID, desiredValue | limitValue}`; Tabela 10, `tableUUID` `0IHX41YEUXXD`; Pix de R$ 300 a R$ 5.000, 2 a 12 parcelas.
- Conta: fator = 0,5479 + 0,003·n; parcela = valor·(1+fator)/n; IOF = valor·(0,0038 + 0,00246·n). Modo limite: valor = limite/(1+fator), teto R$ 5.000; limite mínimo aceito R$ 300 (aviso do que falta).
- Checkout (Gyroo): no desktop só QR Code; 6 passos; exige RG/CNH original; pedido REAL (dono testou o passo 1 e a Gyroo só registra a proposta no fim do cadastro). Botão "Ver minha proposta" sem preenchimento do parceiro: avisa e deixa tentar de novo/continuar.
- Site: https://emprestimo.datalabglobal.com, 13 páginas no sitemap. Dados abertos: Kaggle (rodolfodelfino) e Hugging Face (`datalabglobal/pix-no-cartao-tabela-10`, `datalabglobal/taxas-referencia-bcb`).

## Estado (17/11/2026)
- No ar e testado: auditoria completa (links, SEO, a11y, WebKit iPhone 13/SE/desktop, PageSpeed 97–100), correções, barra fixa no celular, campo com milhar/vírgula, menu que fecha fora, botões 44 px, security.txt, twitter:card. PRs 10 a 17 mesclados.
- NÃO verificado: iPhone físico; passos 2–6 do checkout; Umami só do empréstimo (ID compartilhado).

## Próximos Passos
1. Tarefa agendada `gsc-indexacao-emprestimo-2` (17/11 10:00, precisa do Claude aberto): Google (cota estourava em 16/11 e às 6h de 17/11) empréstimo `/custo-cet-iof`, `/taxas-de-referencia`, `/dados-abertos`, depois veículos/simulador (pedido de outra sessão, dono confirmou); confere Bing das 13 (em 16/11 só a home). Ler o relatório e reagendar se bater na cota.
2. Hugging Face: viewer das tabelas não montou (revisão lida só no commit vazio); dono deve reenviar o `README.md` de `publicacao/huggingface/*/` (agora com `configs`).
3. Umami: se o dono criar o site "Empréstimo", trocar o Website ID (layout/gerador, CLAUDE.md, testes).
4. Pendente de aprovação do dono: linha embaixo do botão ("No parceiro você faz o pedido real: 6 passos, com CPF e documento original"), mantendo o texto "Ver minha proposta".
5. Gyroo: 0 propostas até o fim do cadastro; medir interesse pelo evento `cta-pix` (filtro Hostname no Umami).
