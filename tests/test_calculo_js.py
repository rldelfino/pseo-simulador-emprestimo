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
        for campo in ("pix", "total", "parcela", "iof", "jurosMes", "cetAno"):
            assert js[campo] == pytest.approx(py[campo], rel=1e-12, abs=1e-9), (caso, campo)


@pytest.mark.skipif(NODE is None, reason="Node não instalado")
def test_js_formata_em_reais(tmp_path):
    caminho = tmp_path / "calculo.js"
    caminho.write_text(gerador_emprestimo.gerar_calculo_js(), encoding="utf-8")
    codigo = "const P=require(process.argv[1]);console.log(P.pct(148.97));console.log(P.PIX_MAX);"
    saida = subprocess.run([NODE, "-e", codigo, str(caminho)], capture_output=True, text=True, check=True, timeout=30).stdout.split()
    assert saida == ["148,97%", "5000"]
