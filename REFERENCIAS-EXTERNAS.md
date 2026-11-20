# Onde o nome antigo ("Pix no cartão") ainda aparece fora deste repositório

Levantado em 20/11/2026 por leitura (somente leitura; nenhum repositório irmão foi alterado). O nome correto é **Empréstimo pessoal com crédito do cartão**
(texto curto de link: "Empréstimo com crédito do cartão"). O endereço do site continua `https://emprestimo.datalabglobal.com/`. A sessão principal faz estes PRs.
Os arquivos de `paginas_seo/` dos irmãos são gerados: troque no gerador e regere.

## Rodapés ("Outros simuladores")
| Repositório | Arquivo (fonte) | Linha | Texto atual | Trocar por |
|---|---|---|---|---|
| `002-pseo-simulador-imovel` | `gerador.py` | 4291 (`foot_outros`) | `Pix no cartão de crédito` | `Empréstimo com crédito do cartão` |
| `002-pseo-simulador-imovel` | `gerador.py` | 1705, 2112, 3434, 3585, 4388, 4479, 4551 (link com texto `Pix no cartão` na barra de rodapé de cada modelo de página) | `Pix no cartão` | `Empréstimo com crédito do cartão` |
| `003-pseo-simulador-veiculo` | `gerador_veiculos.py` | 1017 e 4097 | `Pix no cartão` | `Empréstimo com crédito do cartão` |
| `006-pseo-simulador-homeequity` | `gerador_homeequity.py` | 349 (`OUTROS_SIMULADORES`) | `Pix no cartão de crédito` | `Empréstimo com crédito do cartão` |
| `007-pseo-simulador-autoequity` | `gerador_autoequity.py` | 358 (`OUTROS_SIMULADORES`) | `Pix no cartão de crédito` | `Empréstimo com crédito do cartão` |
| `008-pseo-simulador-condominio` | `gerador_condominio.py` | 354 (`OUTROS_SIMULADORES`) | `Pix no cartão de crédito` | `Empréstimo com crédito do cartão` |

Depois de trocar, regerar `paginas_seo/` de cada irmão (os testes de rodapé de 006/007/008 podem citar o texto antigo: conferir com `grep -rn "Pix no cart" tests`).

## Hub (`004-hub-site`)
- `llms.txt`, linha 7: `- [Pix no Cartão de Crédito](https://emprestimo.datalabglobal.com/): simulador para receber de R$ 300 a R$ 5.000 via Pix e pagar em 2 a 12 parcelas na fatura do cartão de crédito...` → `- [Empréstimo pessoal com crédito do cartão](...)`: empréstimo pessoal em que o limite do cartão é a fonte do dinheiro (entregue por Pix); de R$ 300 a R$ 5.000, em 2 a 12 parcelas na fatura.
- Cartão do hub (`index.html` e `en/index.html`, linha 115; fonte em `src/home.pt.html` e `src/en.json`): rótulo `Empréstimo via cartão` / `Credit card loan` está certo no espírito; o título `Limite do cartão vira Pix` / `Card limit becomes Pix` e o texto `Receba Pix na conta e pague em até 12x na fatura` sugerem "crédito por Pix": trocar por algo como `Empréstimo com o limite do cartão` / `Loan using your card limit` e `Receba o valor por Pix e pague em até 12x na fatura. Simule antes de decidir.`; o `alt` da imagem (`sim-cartao.webp`) pode ficar. A imagem `img/sim-cartao.webp` e `og-image-pix.png` mostram o visual antigo (conferir se há texto "Pix no cartão" na arte).
- Rodapé "Produtos" (`index.html`, `404.html`, `privacidade/index.html`, `en/index.html`, `en/privacy/index.html`, `en/terms/index.html`): `Empréstimo via cartão` / `Credit card loan` → `Empréstimo com crédito do cartão` / `Loan with card credit`.
- `_redirects` (linhas 1 a 3): `/pix-no-cartao*` → `https://emprestimo.datalabglobal.com/` já existe e pode ficar (links antigos do hub).
- Pasta `pix-no-cartao/` (páginas antigas, inclui `proposta/`, `500-reais` a `5000-reais`), `assets/pixcartao.*.js`, `og-image-pix.png`, `.github/scripts/verificar_tabela_pix.py` e `.github/workflows/verificar-tabela-pix.yml`: restos do produto quando morava no hub. Conferir se ainda são servidos (o `_redirects` os cobre) e se o workflow duplica o `verificar-tabela-emprestimo.yml` deste repositório (provável: aposentar o do hub).
- `sitemap.xml` do hub: sem menção.

## Dados abertos e diretórios (só o dono pode alterar)
- Kaggle: dataset `rodolfodelfino/pix-no-carto-parcela-iof-e-cet-tabela-10` (o endereço guarda o nome antigo; o título passa a ser "Empréstimo com crédito do cartão (Tabela 10)" na próxima versão publicada pelo robô, se o Kaggle aceitar a mudança de título pela API: NÃO verificado).
- Hugging Face: `datalabglobal/pix-no-cartao-tabela-10` (renomear em Settings > Rename; reenviar o `README.md` de `publicacao/huggingface/emprestimo-cartao-tabela-10/`).
- dados.gov.br: usar `publicacao/dados-gov-br/cadastro.md` (já com o nome e os endereços novos dos arquivos; os endereços antigos redirecionam).
- `origem-hub/` (cópia local ignorada pelo git) e o harness (`Documents/Datalab/harness/projects/datalab-global-hub`): nomes antigos só como histórico; `build_static.py` do harness ainda cita `/pix-no-cartao/` no `llms.txt` (pendência antiga).

## Texto de lançamento (curto, sem promessa de aprovação)
> Empréstimo pessoal com crédito do cartão: o limite do seu cartão de crédito é a fonte do dinheiro, que cai por Pix na sua conta (de R$ 300 a R$ 5.000) e é pago em 2 a 12 parcelas na fatura, com juros e IOF. Simule e veja o custo antes de contratar. Crédito caro, sujeito a análise.
