# Simulador do empréstimo pessoal com crédito do cartão — Datalab Global

Site estático em `emprestimo.datalabglobal.com` (Cloudflare Pages). É um empréstimo pessoal em que o limite do cartão de crédito é a fonte do dinheiro, entregue por Pix. Você escolhe o valor (R$ 300 a R$ 5.000) e o prazo (2x a 12x), vê parcela, total na fatura, IOF e CET, e só então abre a proposta no parceiro (depois de uma tela de confirmação).

- Fonte única da conta: `dados/emprestimo-cartao-tabela-esperada.json` (Tabela 10 do parceiro).
- `calculo.py` e `paginas_seo/calculo.js` (gerado) fazem a mesma conta; os testes comparam os dois.
- `verificar_tabela_emprestimo.py` compara a conta com a API do parceiro (workflow semanal).
- CSS escrito à mão em `src/estilo.css` (sem Tailwind nem npm).

## Comandos
```bash
pip install -r requirements-dev.txt
python gerador_emprestimo.py   # gera paginas_seo/ (copia o CSS e coloca a versão ?v= nos arquivos)
python -m pytest -q            # critério de merge: saída 0
python testar_navegador.py     # fora do CI: Chromium + WebKit, computador e celular (precisa do Playwright)
python testar_aleatorio.py     # fora do CI: sessões aleatórias contra calculo.py
python gerar_icones.py         # fora do CI: ícones, logo e og-image (Playwright + Pillow)
```

Python 3.10 (é o que o CI usa). Medição: Umami, sem cookies. Nenhum dado pessoal passa por este site.
