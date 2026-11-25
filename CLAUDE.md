# Simulador do "Empréstimo pessoal com crédito do cartão" — Datalab Global

Idioma: português do Brasil. Estilo: curto, sem jargão, números reais, dizer o que NÃO foi verificado.

## Nome do produto (corrigido em 20/11/2026)
- **Empréstimo pessoal com crédito do cartão**: um empréstimo pessoal em que o limite do cartão de crédito é a fonte do dinheiro, entregue por Pix. O total (valor + juros + IOF) é lançado no limite do cartão e parcelado na fatura (2 a 12x).
- NUNCA "Pix no cartão", "Pix com cartão" nem "crédito por Pix" (induzem a erro). "Pix" só descreve como o dinheiro chega (chave Pix em nome da pessoa). Os nomes errados aparecem uma única vez, entre aspas, na FAQ da home que os corrige (há teste que barra em qualquer outro lugar).
- O que NÃO foi confirmado: como o emissor libera o limite conforme as parcelas são pagas (regra do emissor; o texto diz para confirmar com o banco).

## Regras fixas
- **Graphify primeiro, sempre, sem o dono pedir.** Antes de ler arquivo/grep: `graphify update .` e `graphify query "..."`. Se pular, avisar na hora.
- Sem gastar dinheiro. Sem postar nem mandar mensagem a pessoas. Cadastro em diretórios/dados abertos é permitido (dono dispensou o gov.br).
- LGPD: nada de CPF/telefone em log, teste ou arquivo. Fluxo do parceiro só com dados de teste do dono.
- Mensagem agnóstica sobre o parceiro: "um parceiro de crédito"/"correspondente bancário", sem citar o nome dele nem de bancos (no código fica só o endereço do checkout). Sem ranking nem "Banco A × Banco B". **Exceção liberada pelo dono em 25/11/2026:** a página `/taxas-por-banco` cita instituições, só com dado público do Banco Central (crédito pessoal não consignado e cartão parcelado, média de 30 dias, ≥15 janelas, ordem ALFABÉTICA, sem ranking, com aviso de que não é oferta); o teste `test_nenhum_banco_citado_e_nada_de_ranking` pula só essa página. Dados: `taxas_bancos.py`, `dados/taxas_por_banco.csv` (atualizado por `etl_taxas_referencia.py`, robô semanal) e cópia em `/dados/taxas-por-banco.csv`. A fonte de nomes é o BCB; ajustes de nome em `taxas_bancos._NOMES`. SEM divulgação de comissão em nenhum lugar (rodapé, Sobre, Termos, FAQ, llms.txt): o dono mandou tirar em 21/11/2026, igual ao 006; fica só o link de redirecionamento do parceiro (`rel="noopener sponsored"`); teste em `tests/test_conteudo.py` barra "comissão"/"remuneração".
- Medição: Umami (sem cookies), Website ID `ba3c0b88-59e8-47dd-866d-0b05e5e7dae9` (COMPARTILHADO com imobiliário e veículos; no Umami filtrar por Hostname). Dados abertos CC BY 4.0. Sem AdSense.
- Sem segredo em arquivo/GitHub (token do Kaggle = segredo `KAGGLE_API_TOKEN` do repo). Sem identificar modelo de IA em commits/PRs (só as linhas de atribuição que o sistema mandar).
- Merge só com `pytest` saindo 0 (não usar `pytest | tail`). Python 3.10 (sem f-string aninhado). Fluxo de alteração: branch → PR → merge (Windows mostra avisos LF/CRLF, normais).
- CSP: sem `style=` nem script inline. Barras/rosca são SVG com atributos; o preenchimento dos sliders usa `data-p` (0 a 100) definido por JS e uma regra de CSS por valor.
- **Paleta: roxo/púrpura** (violet; `--ac:#a78bfa`). Verde é do imobiliário, azul dos veículos, azul-petróleo do Home Equity: não usar aqui.
- Máximo ~30 páginas indexáveis, cada uma com conteúdo próprio. Sem grade de páginas quase iguais.
- Não baixar arquivo sem permissão do dono. Não mandar evento de teste ao Umami (nos testes o Umami é substituído por um stub e a API do parceiro é simulada).
- Pedir indexação (Google/Bing) só para URL nova ou desconhecida; repetir não adianta.

## Comandos
- Gerar: `python gerador_emprestimo.py` (saída em `paginas_seo/`, Cloudflare Pages sem build). O CSS é escrito à mão em `src/estilo.css` e copiado para `styles.css` (sem Tailwind/npm desde 20/11/2026). O hash `?v=` de CSS/JS é calculado na geração.
- Testes: `python -m pytest -q` (129). No navegador, fora do CI (Playwright): `python testar_navegador.py [--externos]` (Chromium + WebKit, computador e celular; servidor local aplica `_headers` e `_redirects`; Umami e API do parceiro simulados) e `python testar_aleatorio.py` (sessões aleatórias contra `calculo.py`).
- Ícones, logo e imagem de compartilhamento: `python gerar_icones.py` (Playwright + Pillow; logo em SVG no `LOGO` de `layout.py`, molde `src/og-image.html`). Pacote de publicação: `python publicacao.py`.
- Fontes: `layout.py` (HTML), `conteudo.py` (textos, títulos ≤ 60 caracteres), `src/simulador.js`, `src/menu.js`, `src/estilo.css`, `gerador_emprestimo.py`. `gh` portátil: `C:\Users\rldel\tools\gh\app\bin` (logado como rldelfino).
- Robô semanal `.github/workflows/atualiza_taxas.yml` (seg 08:00 UTC): taxas BCB, rebuild, testes, IndexNow, commit de `dados paginas_seo publicacao` e, por último, Kaggle (Python 3.12, `continue-on-error`). CI (`ci.yml`) roda build, pytest e `git diff --exit-code dados/datas_paginas.json`. `verificar-tabela-emprestimo.yml` confere a Tabela 10 com a API do parceiro.
- **IndexNow depois do deploy** (quem mescla roda, da `main` atualizada): `python indexnow.py` (envia todas as URLs do sitemap, incluindo a página nova `/emprestimo-com-cartao-ou-outro-credito`).

## Origem
`origem-hub/` é cópia (13/11/2026) do código que nasceu no harness (`Documents/Datalab/harness/projects/datalab-global-hub`); o dono não mexe mais lá. Referência: `origem-hub/pixcartao/components/calculo.ts`, `proposta.ts`, `tools/` (nomes antigos, só histórico).

## Fatos do produto
- API: `POST https://api.triagem.digital/proposals/simulator` `{parcels, tableUUID, desiredValue | limitValue}`; Tabela 10, `tableUUID` `0IHX41YEUXXD`; valor recebido de R$ 300 a R$ 5.000, 2 a 12 parcelas. Fonte única dos números: `dados/emprestimo-cartao-tabela-esperada.json` (`valor_max`, fatores, CET).
- Conta: fator = 0,5479 + 0,003·n; parcela = valor·(1+fator)/n; IOF = valor·(0,0038 + 0,00246·n). Modo limite: valor = limite/(1+fator), teto R$ 5.000; limite mínimo R$ 300 (aviso do que falta). `calculo.simular` devolve `receber`, `total`, `parcela`, `iof`, `jurosMes`, `cetAno`.
- "Já tem uma proposta?": `calculo.taxa_implicita` = `DatalabEmprestimo.taxaImplicita` (juros ao mês de n parcelas iguais que valem o valor recebido; sem tarifas). Pela mesma conta a Tabela 10 dá de 0,4 a 0,5 ponto a mais que o "juros ao mês" tabelado pelo parceiro (método diferente, NÃO reproduzido; teste fixa a faixa 0,3–0,7). A tela compara proposta e Tabela 10 pela mesma conta e cita o número do parceiro.
- Checkout (parceiro): no desktop só QR Code; 6 passos; exige RG/CNH original; pedido REAL. Fluxo no site: "Ver minha proposta" abre a tela de confirmação (`<dialog>`), "Continuar para o parceiro" pede a simulação à API e abre o checkout pré-preenchido na mesma aba; se a API falhar, avisa e oferece "Continuar mesmo assim" (checkout sem código).
- Site: https://emprestimo.datalabglobal.com, 13 páginas no sitemap. Dados abertos: arquivos `emprestimo-cartao-tabela-10.*` e `taxas-referencia-bcb.*` em `/dados/`; Kaggle (`rodolfodelfino/pix-no-carto-parcela-iof-e-cet-tabela-10`: o endereço guarda o nome antigo e não dá para mudar; título, subtítulo e descrição já foram trocados em 21/11/2026) e Hugging Face (`datalabglobal/emprestimo-cartao-tabela-10`, renomeado em 21/11/2026 com README e CSV novos; o endereço antigo redireciona; `datalabglobal/taxas-referencia-bcb`).
- Redirecionamentos 301 (`paginas_seo/_redirects`, gerado): `/pix-no-cartao-ou-outro-credito` (e `.html`) → `/emprestimo-com-cartao-ou-outro-credito`; arquivos `/dados/*pix-no-cartao-tabela-10*` → `/dados/*emprestimo-cartao-tabela-10*`.
- Resultado do simulador: `calculo.js` (gerado) leva `referencias` = últimas médias do BCB (juros ao mês vs juros do empréstimo, nunca CET vs juros); URL compartilhável `/?modo=valor|limite&valor=|limite=&parcelas=[&prop=]` (só número, canonical = home); a última simulação fica em `sessionStorage` (`emp-sim`) para o botão "Voltar à simulação" das páginas internas.
- **Eventos Umami (renomeados em 20/11/2026)**: `usou-simulador-emprestimo` (era `usou-simulador-pix`), `abriu-confirmacao` (novo), `cta-parceiro` (era `cta-pix`; agora só ao confirmar), `cta-parceiro-sem-preenchimento` (era `cta-pix-sem-preenchimento`), `copiou-link`, `usou-proposta-propria` (novo). Os nomes antigos continuam no histórico do Umami; somar manualmente.
- Data por página: `dados/datas_paginas.json` (hash + data). Gerador renderiza com data fixa e sem `?v=`; só leva "hoje" se o hash mudou. Vale para "Atualizado em", `lastmod`, `dateModified`, `llms.txt`; feed usa a data da última entrada. Se o CI falhar nesse arquivo: rodar o gerador e commitar.
- Rodapé: coluna "Outros simuladores" (`OUTROS_SIMULADORES` em `gerador_emprestimo.py`): imobiliário, veículos, Home Equity, Auto Equity, Condomínio e o hub.
- Segurança/acessibilidade: CSP com `object-src 'none'`, COOP, HSTS, XFO DENY, nosniff; cores de texto herdadas do template do 006 (contraste não medido de novo aqui); alvos de toque 44 px; lista do BCB com `aria-live="off"`.
- Arquivo de verificação do Yandex Webmaster: `paginas_seo/yandex_90c15c3be650b0ed.html` (conteúdo exato; o gerador não mexe nele e o `.gitignore` não o barra).
- `REFERENCIAS-EXTERNAS.md`: onde o nome antigo ainda aparece nos repositórios irmãos (a sessão principal faz esses PRs).

## Estado (20/11/2026)
- Nome corrigido e template novo aplicados no PR da branch `renomeia-emprestimo-cartao-template-novo` (aguarda merge). Antes: PRs 10 a 24 mesclados.
- Google/Bing (17/11): home e `/custo-cet-iof` rastreadas, NÃO indexadas no Google; Bing só a home. Reinspecionar depois do deploy; a URL `/emprestimo-com-cartao-ou-outro-credito` é nova (pedir indexação uma vez; a antiga redireciona).
- NÃO verificado: iPhone físico; passos 2–6 do checkout do parceiro; Umami só do empréstimo (ID compartilhado); robô semanal rodando com o código novo; o porquê da diferença de 0,4 ponto entre a taxa tabelada e a calculada; "pagar a mais"/antecipar parcelas (não há regra conhecida do parceiro/emissor, não foi construído).
- `src/estilo.css` é a cópia do template comum (Home Equity) recolorida em roxo e traz regras que este site não usa (comparativos, amortização); não afetam nada.

## Próximos Passos
1. Depois do merge e do deploy: rodar `python indexnow.py`; conferir `/pix-no-cartao-ou-outro-credito` → 301; reinspecionar Google/Bing em 3–7 dias.
2. (feito em 21/11/2026) Kaggle: título/descrição trocados (slug fica); Hugging Face: renomeado e README/CSV reenviados. O robô semanal sobe a versão nova do Kaggle (arquivo `emprestimo-cartao-tabela-10.csv`).
3. Segunda 23/11 (após 08:00 UTC): conferir o robô semanal; `lastmod` das páginas sem mudança deve ficar na data do merge (só taxas e home podem avançar).
4. Umami: o plano grátis só permite 1 site ("Website limit reached", testado em 21/11/2026); por isso o ID é compartilhado. Só muda com plano pago (dono decide).
5. Parceiro: 0 propostas até o fim do cadastro; medir `abriu-confirmacao` → `cta-parceiro` e `copiou-link` (filtro Hostname no Umami).
6. Sessão principal: PRs de rodapé/hub nos irmãos com o nome novo (lista em `REFERENCIAS-EXTERNAS.md`).
