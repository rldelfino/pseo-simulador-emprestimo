"""O cálculo do navegador (calculo.js) tem que ser idêntico ao de calculo.py."""
import json
import os
import shutil
import subprocess

import pytest

import calculo
import gerador_emprestimo

NODE = shutil.which("node")

CASOS = [("valor", v, 0, n) for v in (300, 500, 1000, 2500, 4999.5, 5000) for n in calculo.PARCELAS] + \
        [("limite", 0, lim, n) for lim in (500, 2000, 8000, 20000) for n in calculo.PARCELAS]

SCRIPT = """
const P = require(process.argv[2]);
const casos = JSON.parse(process.argv[3]);
console.log(JSON.stringify(casos.map(c => P.simular(c[0], c[1], c[2], c[3]))));
"""


@pytest.mark.skipif(NODE is None, reason="Node não instalado")
def test_js_igual_ao_python(tmp_path):
    caminho = tmp_path / "calculo.js"
    caminho.write_text(gerador_emprestimo.gerar_calculo_js(), encoding="utf-8")
    script = tmp_path / "rodar.js"
    script.write_text(SCRIPT, encoding="utf-8")
    saida = subprocess.run([NODE, str(script), str(caminho), json.dumps(CASOS)],
                           capture_output=True, text=True, check=True, timeout=60).stdout
    resultados = json.loads(saida)
    assert len(resultados) == len(CASOS)
    for caso, js in zip(CASOS, resultados):
        py = calculo.simular(*caso)
        for campo in ("receber", "total", "parcela", "iof", "jurosMes", "cetAno"):
            assert js[campo] == pytest.approx(py[campo], rel=1e-12, abs=1e-9), (caso, campo)


@pytest.mark.skipif(NODE is None, reason="Node não instalado")
def test_js_formata_em_reais(tmp_path):
    caminho = tmp_path / "calculo.js"
    caminho.write_text(gerador_emprestimo.gerar_calculo_js(), encoding="utf-8")
    codigo = "const P=require(process.argv[1]);console.log(P.pct(148.97));console.log(P.VALOR_MAX);"
    saida = subprocess.run([NODE, "-e", codigo, str(caminho)], capture_output=True, text=True, check=True, timeout=30).stdout.split()
    assert saida == ["148,97%", "5000"]


@pytest.mark.skipif(NODE is None, reason="Node não instalado")
def test_js_leva_as_medias_do_bcb_iguais_ao_csv(tmp_path):
    caminho = tmp_path / "calculo.js"
    caminho.write_text(gerador_emprestimo.gerar_calculo_js(), encoding="utf-8")
    codigo = "const P=require(process.argv[1]);console.log(JSON.stringify(P.referencias));"
    refs = json.loads(subprocess.run([NODE, "-e", codigo, str(caminho)], capture_output=True, text=True, encoding="utf-8", check=True, timeout=30).stdout)
    esperado = gerador_emprestimo.referencias_bcb()
    assert refs == esperado and len(refs) == 3
    for r in refs:
        assert r["am"] < r["aa"] and 10 < r["aa"] < 1500  # mensal equivalente é menor que a taxa anual; valor plausível
        assert r["mes"].split(" de ")[1].isdigit()


@pytest.mark.skipif(NODE is None, reason="Node não instalado")
def test_taxa_implicita_js_igual_ao_python(tmp_path):
    caminho = tmp_path / "calculo.js"
    caminho.write_text(gerador_emprestimo.gerar_calculo_js(), encoding="utf-8")
    casos = [(1000, 140, 12), (1000, 600, 2), (300, 40, 9), (5000, 700, 12), (1000, 80, 12), (0, 10, 3)]
    codigo = "const P=require(process.argv[1]);console.log(JSON.stringify(JSON.parse(process.argv[2]).map(c=>P.taxaImplicita(c[0],c[1],c[2]))));"
    saida = subprocess.run([NODE, "-e", codigo, str(caminho), json.dumps(casos)], capture_output=True, text=True, check=True, timeout=30).stdout
    for caso, js in zip(casos, json.loads(saida)):
        py = calculo.taxa_implicita(*caso)
        if py is None:
            assert js is None, caso
        else:
            assert js == pytest.approx(py, rel=1e-12), caso
