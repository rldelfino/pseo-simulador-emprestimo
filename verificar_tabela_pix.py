# -*- coding: utf-8 -*-
"""Confere se a conta do simulador "Pix no cartão" ainda bate com a Tabela 10 do parceiro.

O simulador (calculo.py e paginas_seo/calculo.js) calcula parcela, IOF, juros e CET localmente; se o parceiro mudar a
tabela, a página passaria a mostrar números errados sem ninguém perceber. Este script pergunta à API do parceiro o
resultado de R$ 1.000 em cada prazo (2x a 12x) e os limites (valor máximo e parcelas), e compara com o esperado
(dados/pix-tabela-esperada.json, a mesma fonte usada por calculo.py e calculo.js — uma fonte só).

Sai com código 1 se algo mudou (o GitHub Actions marca a execução como falha e manda e-mail ao dono do repositório).
Só biblioteca padrão do Python.

Uso:  python verificar_tabela_pix.py [caminho/pix-tabela-esperada.json]
"""
import json
import os
import sys
import urllib.request

API = "https://api.triagem.digital/proposals/simulator"
VALOR = 1000.0
TOL_REAIS = 0.02     # arredondamento de centavos
TOL_PCT = 0.02       # pontos percentuais em juros/CET


def post(corpo):
    req = urllib.request.Request(API, data=json.dumps(corpo).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (DatalabVerificador)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (DatalabVerificador)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def main():
    caminho = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados", "pix-tabela-esperada.json")
    esp = json.load(open(caminho, encoding="utf-8"))
    problemas = []

    lim = get(f"{API}/limits?tableUUID={esp['table_uuid']}")
    if lim.get("maxNetAmount") != esp["pix_max"]:
        problemas.append(f"valor máximo mudou: {esp['pix_max']} -> {lim.get('maxNetAmount')}")
    max_parcelas = max(int(k) for k in esp["cet"])
    if int(lim.get("maxParcels") or 0) != max_parcelas:
        problemas.append(f"parcelas máximas mudaram: {max_parcelas} -> {lim.get('maxParcels')}")

    for n_txt, cet in sorted(esp["cet"].items(), key=lambda kv: int(kv[0])):
        n = int(n_txt)
        r = post({"parcels": n, "tableUUID": esp["table_uuid"], "desiredValue": VALOR})
        fator = esp["fator_base"] + esp["fator_por_parcela"] * n
        parcela = VALOR * (1 + fator) / n
        iof = VALOR * (esp["iof_fixo"] + esp["iof_por_parcela"] * n)
        checagens = [
            ("parcela", parcela, r.get("parcelAmount"), TOL_REAIS),
            ("total na fatura", VALOR * (1 + fator), r.get("grossAmount"), TOL_REAIS),
            ("IOF", iof, r.get("iofAmount"), TOL_REAIS),
            ("juros ao mês", cet["monthly"], r.get("interestMonthly"), TOL_PCT),
            ("CET ao ano", cet["annual"], r.get("cetAnnual"), TOL_PCT),
        ]
        for nome, nosso, deles, tol in checagens:
            if deles is None or abs(float(nosso) - float(deles)) > tol:
                problemas.append(f"{n}x — {nome}: nosso {nosso:.2f}, parceiro {deles}")
        if r.get("tableName") and r["tableName"] != esp["table_name"]:
            problemas.append(f"{n}x — tabela mudou de nome: {esp['table_name']} -> {r['tableName']}")

    if problemas:
        print("A TABELA DO PIX NO CARTÃO MUDOU — atualize dados/pix-tabela-esperada.json e rode gerador_emprestimo.py:")
        for p in problemas:
            print(" -", p)
        return 1
    print(f"OK: a conta do simulador bate com a {esp['table_name']} do parceiro em todos os prazos (2x a 12x) e nos limites.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
