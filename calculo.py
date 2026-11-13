"""Conta do Pix no cartão (Tabela 10 do parceiro). Fonte única: dados/pix-tabela-esperada.json.

O mesmo cálculo roda no navegador (paginas_seo/calculo.js), gerado a partir do mesmo JSON por
gerador_emprestimo.py. Os testes comparam os dois lados e a API do parceiro.
"""
import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
CAMINHO_TABELA = os.path.join(AQUI, "dados", "pix-tabela-esperada.json")
PIX_MIN = 300


def carregar_tabela(caminho=CAMINHO_TABELA):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


TABELA = carregar_tabela()
PIX_MAX = TABELA["pix_max"]
PARCELAS = sorted(int(n) for n in TABELA["cet"])


def simular(modo, valor, limite, parcelas, tabela=TABELA):
    """modo 'valor': quanto cai no Pix. modo 'limite': quanto cabe no limite do cartão."""
    fator = tabela["fator_base"] + tabela["fator_por_parcela"] * parcelas
    if modo == "valor":
        pix = valor
    else:
        pix = min(limite / (1 + fator), tabela["pix_max"])
    total = pix * (1 + fator)
    cet = tabela["cet"][str(parcelas)]
    return {
        "pix": pix,
        "total": total,
        "parcela": total / parcelas,
        "iof": pix * (tabela["iof_fixo"] + tabela["iof_por_parcela"] * parcelas),
        "jurosMes": cet["monthly"],
        "cetAno": cet["annual"],
    }
