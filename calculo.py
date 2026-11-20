"""Conta do empréstimo pessoal com crédito do cartão (Tabela 10 do parceiro). Fonte única: dados/emprestimo-cartao-tabela-esperada.json.

O mesmo cálculo roda no navegador (paginas_seo/calculo.js), gerado a partir do mesmo JSON por
gerador_emprestimo.py. Os testes comparam os dois lados e a API do parceiro.
"""
import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
CAMINHO_TABELA = os.path.join(AQUI, "dados", "emprestimo-cartao-tabela-esperada.json")
VALOR_MIN = 300


def carregar_tabela(caminho=CAMINHO_TABELA):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


TABELA = carregar_tabela()
VALOR_MAX = TABELA["valor_max"]
PARCELAS = sorted(int(n) for n in TABELA["cet"])


def simular(modo, valor, limite, parcelas, tabela=TABELA):
    """modo 'valor': quanto cai na conta (por Pix). modo 'limite': quanto cabe no limite do cartão."""
    fator = tabela["fator_base"] + tabela["fator_por_parcela"] * parcelas
    if modo == "valor":
        receber = valor
    else:
        receber = min(limite / (1 + fator), tabela["valor_max"])
    total = receber * (1 + fator)
    cet = tabela["cet"][str(parcelas)]
    return {
        "receber": receber,
        "total": total,
        "parcela": total / parcelas,
        "iof": receber * (tabela["iof_fixo"] + tabela["iof_por_parcela"] * parcelas),
        "jurosMes": cet["monthly"],
        "cetAno": cet["annual"],
    }


def taxa_implicita(receber, parcela, n):
    """Juros ao mês (em %) de um empréstimo em que você recebe `receber` e paga `n` parcelas iguais de `parcela` (taxa que zera o valor presente).
    Mesma conta de DatalabEmprestimo.taxaImplicita (calculo.js). Devolve None se a parcela não cobre nem o valor recebido (taxa negativa)."""
    if receber <= 0 or parcela * n <= receber:
        return None
    lo, hi = 0.0, 5.0
    for _ in range(200):
        i = (lo + hi) / 2
        vp = parcela * (1 - (1 + i) ** -n) / i if i > 0 else parcela * n
        if vp > receber:
            lo = i
        else:
            hi = i
    return (lo + hi) / 2 * 100
