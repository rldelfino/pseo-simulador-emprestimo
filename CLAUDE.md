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
- Não baixar arquivo sem permissão do dono. Não mandar evento de teste ao Umami (contamina os números; em testes de navegador bloquear `umami` e `api.triagem.digital`).
- Pedir indexação (Google/Bing) só para URL nova ou desconhecida; repetir não adianta.

## Comandos
- Build: `python gerador_emprestimo.py` → `npm run build:css` → `python gerador_emprestimo.py` (o hash `?v=` do CSS/JS é calculado na geração).
- Testes: `python -m pytest -q` (105). Pacote de publicação: `python publicacao.py`. Imagem de compartilhamento: `python gerar_og_image.py` (molde `src/og-image.html`, precisa do Playwright, fora do CI).
- Fontes: `layout.py` (HTML), `conteudo.py` (textos, títulos ≤ 60 caracteres), `src/simulador.js`, `src/menu.js`, `gerador_emprestimo.py`. Saída: `paginas_seo/` (Cloudflare Pages, sem build). `gh` portátil: `C:\Users\rldel\tools\gh\app\bin` (logado como rldelfino).
- Robô semanal `.github/workflows/atualiza_taxas.yml` (seg 08:00 UTC): taxas BCB, rebuild, testes, IndexNow, commit de `dados paginas_seo publicacao` e, por último, Kaggle (Python 3.12, `continue-on-error`). CI (`ci.yml`) roda build, pytest e `git diff --exit-code dados/datas_paginas.json`.

## Origem
`origem-hub/` é cópia (13/11/2026) do código que nasceu no harness (`Documents/Datalab/harness/projects/datalab-global-hub`); o dono não mexe mais lá. Referência: `origem-hub/pixcartao/components/calculo.ts`, `proposta.ts`, `tools/`.

## Fatos do produto
- API: `POST https://api.triagem.digital/proposals/simulator` `{parcels, tableUUID, desiredValue | limitValue}`; Tabela 10, `tableUUID` `0IHX41YEUXXD`; Pix de R$ 300 a R$ 5.000, 2 a 12 parcelas.
- Conta: fator = 0,5479 + 0,003·n; parcela = valor·(1+fator)/n; IOF = valor·(0,0038 + 0,00246·n). Modo limite: valor = limite/(1+fator), teto R$ 5.000; limite mínimo R$ 300 (aviso do que falta).
- Checkout (Gyroo): no desktop só QR Code; 6 passos; exige RG/CNH original; pedido REAL (Gyroo só registra a proposta no fim do cadastro). Botão "Ver minha proposta" sem preenchimento do parceiro: avisa e deixa tentar de novo/continuar.
- Site: https://emprestimo.datalabglobal.com, 13 páginas no sitemap. Dados abertos: Kaggle (rodolfodelfino) e Hugging Face (`datalabglobal/pix-no-cartao-tabela-10`, `datalabglobal/taxas-referencia-bcb`).
- Resultado do simulador: `calculo.js` (gerado) leva `referencias` = últimas médias do BCB (juros ao mês vs juros do Pix, nunca CET vs juros); URL compartilhável `/?modo=valor|limite&valor=|limite=&parcelas=` (só número, canonical = home); eventos Umami: `usou-simulador-pix`, `cta-pix`, `cta-pix-sem-preenchimento`, `copiou-link`.
- Data por página: `dados/datas_paginas.json` (hash + data). Gerador renderiza com data fixa e sem `?v=`; só leva "hoje" se o hash mudou. Vale para "Atualizado em", `lastmod`, `dateModified`, `llms.txt`; feed usa a data da última entrada. Se o CI falhar nesse arquivo: rodar o gerador e commitar.
- Rodapé: coluna "Outros simuladores" (`OUTROS_SIMULADORES` em `gerador_emprestimo.py`). simulador, veiculos e hub linkam o empréstimo direto (hub passou a linkar direto em 17/11, `_redirects` do hub mantido).
- Segurança/acessibilidade (auditoria 17/11): CSP com `object-src 'none'`, COOP, texto pequeno em `slate-400` (slate-500 reprova contraste), alvos de toque 44 px, lista do BCB com `aria-live="off"`.

## Estado (17/11/2026)
- No ar, testado e mesclado: PRs 10 a 22 (empréstimo), 30 (veiculos), 34 (imobiliário), 3 (hub). pytest 105 verdes, CI verde.
- Google: home e `/custo-cet-iof` rastreadas, NÃO indexadas ("rastreada, não indexada", comum em subdomínio novo); `/taxas-de-referencia` e `/dados-abertos` tiveram indexação pedida em 17/11 (eram desconhecidas). Sitemap enviado e lido (13). Outras 9 páginas não inspecionadas.
- Bing: só a home indexada; as outras 12 estavam "Discovered but not crawled", indexação pedida em 17/11 (cota 95/dia) + IndexNow 200. Sitemap lido (13).
- NÃO verificado: iPhone físico; passos 2–6 do checkout; Umami só do empréstimo (ID compartilhado); robô semanal rodando com o código novo.

## Próximos Passos
1. Em ~3–7 dias reinspecionar Google (GSC: caixa "Inspecionar" do topo, propriedade de domínio `sc-domain:datalabglobal.com`) e Bing (`bing.com/webmasters/urlinspection?siteUrl=https%3A%2F%2Fwww.datalabglobal.com%2F&urlToInspect=<URL com :// e / codificados duas vezes>`) via Claude in Chrome (dono logado). Ver quais das 13 entraram; não repetir pedido de URL já rastreada.
2. Segunda 24/11 (após 08:00 UTC): conferir o robô semanal; `lastmod` das páginas sem mudança deve ficar em 2026-11-17 (só taxas e home podem avançar) e `dados/datas_paginas.json` commitado pelo robô.
3. Hugging Face: viewer das tabelas não montou; dono deve reenviar o `README.md` de `publicacao/huggingface/*/` (com `configs`).
4. Umami: se o dono criar o site "Empréstimo", trocar o Website ID (layout/gerador, CLAUDE.md, testes).
5. Gyroo: 0 propostas até o fim do cadastro; medir interesse por `cta-pix` e `copiou-link` (filtro Hostname no Umami).
6. Fora de escopo, avisar o dono: `taxas-financiamento-veiculos-outubro-2024.html` é arquivo órfão ainda no ar em veiculos; `build_static.py` do harness ainda cita `/pix-no-cartao/` na linha do `llms.txt` (arquivo com alterações pendentes do dono); repos irmãos não têm CI de PR.
