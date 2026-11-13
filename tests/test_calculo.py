"""Fixa a conta do Pix no cartão (Tabela 10): parcela, total, IOF, juros e CET."""
import json
import os

import pytest

import calculo

# Valores conferidos na API do parceiro em 13/11/2026 (R$ 1.000 em 12x): parcela 131,99, total 1.583,90, IOF 33,32.


def test_prazos_e_limites():
    assert calculo.PARCELAS == list(range(2, 13))
    assert calculo.PIX_MIN == 300
    assert calculo.PIX_MAX == 5000


def test_r1000_em_12x_bate_com_a_api():
    r = calculo.simular("valor", 1000, 0, 12)
    assert r["total"] == pytest.approx(1583.90, abs=0.005)
    assert r["parcela"] == pytest.approx(131.99, abs=0.005)
    assert r["iof"] == pytest.approx(33.32, abs=0.005)
    assert r["jurosMes"] == 7.49
    assert r["cetAno"] == 148.97


def test_r1000_em_2x():
    r = calculo.simular("valor", 1000, 0, 2)
    assert r["total"] == pytest.approx(1553.90, abs=0.005)
    assert r["parcela"] == pytest.approx(776.95, abs=0.005)
    assert r["iof"] == pytest.approx(8.72, abs=0.005)
    assert r["jurosMes"] == 34.64
    assert r["cetAno"] == 3621.21


@pytest.mark.parametrize("n", range(2, 13))
def test_formula_contra_o_json(n):
    esp = json.load(open(os.path.join(os.path.dirname(calculo.__file__), "dados", "pix-tabela-esperada.json"), encoding="utf-8"))
    fator = esp["fator_base"] + esp["fator_por_parcela"] * n
    r = calculo.simular("valor", 2500, 0, n)
    assert r["parcela"] == pytest.approx(2500 * (1 + fator) / n)
    assert r["iof"] == pytest.approx(2500 * (esp["iof_fixo"] + esp["iof_por_parcela"] * n))
    assert r["jurosMes"] == esp["cet"][str(n)]["monthly"]
    assert r["cetAno"] == esp["cet"][str(n)]["annual"]


def test_mais_parcelas_custa_mais_no_total_e_menos_por_mes():
    rs = [calculo.simular("valor", 1000, 0, n) for n in calculo.PARCELAS]
    totais = [r["total"] for r in rs]
    parcelas = [r["parcela"] for r in rs]
    assert totais == sorted(totais)
    assert parcelas == sorted(parcelas, reverse=True)


def test_modo_limite_cabe_no_limite_e_respeita_o_teto():
    r = calculo.simular("limite", 0, 2000, 12)
    assert r["total"] == pytest.approx(2000)
    assert r["pix"] == pytest.approx(2000 / 1.5839)
    teto = calculo.simular("limite", 0, 10000, 12)
    assert teto["pix"] == 5000


def test_cet_decresce_com_o_prazo():
    anual = [calculo.simular("valor", 1000, 0, n)["cetAno"] for n in calculo.PARCELAS]
    assert anual == sorted(anual, reverse=True)
