# Simulador de empréstimo via cartão ("Pix no cartão") — Datalab Global

Site estático em `emprestimo.datalabglobal.com` (Cloudflare Pages). Você escolhe o valor (R$ 300 a R$ 5.000) e o prazo (2x a 12x), vê parcela, total na fatura, IOF e CET, e só então abre a proposta no parceiro.

- Fonte única da conta: `dados/pix-tabela-esperada.json` (Tabela 10 do parceiro).
- `calculo.py` e `paginas_seo/calculo.js` (gerado) fazem a mesma conta; os testes comparam os dois.
- `verificar_tabela_pix.py` compara a conta com a API do parceiro (workflow semanal).

## Comandos
```bash
pip install -r requirements-dev.txt
npm ci
python gerador_emprestimo.py   # gera paginas_seo/
npm run build:css              # compila o Tailwind
python -m pytest -q            # critério de merge: saída 0
```

Python 3.10 (é o que o CI usa). Medição: Umami, sem cookies. Nenhum dado pessoal passa por este site.
