"""Taxas por instituição financeira (Banco Central), usadas na página "Taxas por banco".

Fonte: BCB, "Taxas de juros de operações de crédito por instituição financeira" (serviço Olinda, `taxaJuros`, conjunto
`TaxasJurosDiariaPorInicioPeriodo`), licença ODbL. Duas modalidades de pessoa física, as mais próximas do empréstimo com crédito do cartão:
crédito pessoal não consignado e cartão de crédito parcelado (ambas prefixadas).

Cada linha do BCB é uma JANELA móvel (5 dias úteis) com a taxa média daquela instituição. Aqui juntamos as janelas dos últimos 30 dias
(a partir da janela mais recente) em uma média simples por instituição, e só mostramos quem apareceu em pelo menos MIN_JANELAS delas
(para não mostrar quem operou uma vez só no mês). A média é SIMPLES, sem peso por volume: o BCB não publica o volume por instituição nesse conjunto.

Os dados ficam em dados/taxas_por_banco.csv (uma linha por modalidade e instituição), atualizado por etl_taxas_referencia.py.
"""
import csv
import datetime
import os
import re
import statistics

AQUI = os.path.dirname(os.path.abspath(__file__))
CAMINHO_CSV = os.path.join(AQUI, "dados", "taxas_por_banco.csv")
CABECALHO = ["modalidade", "cnpj8", "instituicao", "taxa_am", "taxa_aa", "janelas", "periodo_inicio", "periodo_fim"]
MODALIDADES = [
    dict(chave="pessoal", nome="Crédito pessoal não consignado", bcb="Crédito pessoal não consignado - Prefixado"),
    dict(chave="cartao-parcelado", nome="Cartão de crédito parcelado", bcb="Cartão de crédito - parcelado - Prefixado"),
]
URL_API = "https://olinda.bcb.gov.br/olinda/servico/taxaJuros/versao/v2/odata/TaxasJurosDiariaPorInicioPeriodo"
URL_FONTE = "https://www.bcb.gov.br/estatisticas/reporttxjuros"
DIAS_JANELA = 30
MIN_JANELAS = 15          # de ~20 dias úteis no período
FAIXA_AM = (0.3, 25.0)    # fora disso o registro é descartado (protege contra dado quebrado)
MIN_INSTITUICOES = 15     # abaixo disso (em qualquer modalidade) o ETL não troca o CSV

# Os cinco maiores bancos de varejo do país (CNPJ-base de 8 dígitos). Critério fixo e público; a ordem na tabela é alfabética, não por taxa.
GRANDES = {
    "00000000": "Banco do Brasil",
    "00360305": "Caixa Econômica Federal",
    "60701190": "Itaú Unibanco",
    "60872504": "Itaú Unibanco",        # holding: aparece no cartão parcelado
    "60746948": "Bradesco",
    "90400888": "Santander",
}

_NOMES = {
    "02038232": "Sicoob", "30306294": "BTG Pactual", "00416968": "Inter", "58160789": "Safra", "92702067": "Banrisul", "28127603": "Banestes",
    "13009717": "Banese", "04902979": "Banco da Amazônia", "00000208": "BRB", "59588111": "Votorantim", "09516419": "PicPay",
    "38486817": "BDMG", "07237373": "Banco do Nordeste", "30680829": "Nu Financeira", "31872495": "C6 Bank", "33264668": "XP",
    "71027866": "BS2", "68900810": "Rendimento", "62232889": "Daycoval", "07679404": "Topázio", "17351180": "Triângulo", "11970623": "Senff",
    "07207996": "Bradesco Financiamentos", "04913711": "Banpará", "02682287": "Pan Financeira", "14388334": "Paraná Banco", "43180355": "Pefisa",
    "01858774": "Banco BV", "08357240": "Banco CSF", "06881898": "Financeira Itaú CBD", "61186680": "Banco Bmg", "10264663": "Bancoseguro",
}
_SIGLAS = {"CFI", "SCFI", "BRB", "BS2", "C6", "XP", "RNX", "RPW", "CC", "CCB", "DTVM", "SCD", "SEP"}
_MINUSCULAS = {"DO", "DA", "DE", "DOS", "DAS", "E"}


def nome_amigavel(cnpj8, bruto):
    """Nome para exibir: os cinco grandes e alguns nomes conhecidos vêm de tabelas; o resto é o nome do BCB sem "S.A." e em letras normais."""
    if cnpj8 in GRANDES:
        return GRANDES[cnpj8]
    if cnpj8 in _NOMES:
        return _NOMES[cnpj8]
    n = re.sub(r"(?<![A-Za-z])S[.]?[ ]?/?[ ]?A(?![A-Za-z])[.]?", " ", bruto.strip(), flags=re.I)     # "S.A.", "S/A", "SA" como palavra inteira (nao "SAFRA")
    n = re.sub(r"^BCO(?![A-Za-z])[.]?", "Banco", n, flags=re.I)
    n = re.sub(r"[ ]+", " ", n).strip(" -")
    partes = []
    for w in n.split():
        if w.upper() in _SIGLAS:
            partes.append(w.upper())
        elif w.upper() in _MINUSCULAS:
            partes.append(w.lower())
        else:
            partes.append(w if w == "-" else "-".join(x.capitalize() for x in w.split("-")))
    nome = " ".join(partes)
    return re.sub(r"(?<=[.])([a-z])", lambda m: m.group(1).upper(), nome)     # "J.safra" -> "J.Safra"


def agregar(registros, dias=DIAS_JANELA, min_janelas=MIN_JANELAS):
    """registros: lista de dicts da API (InicioPeriodo, FimPeriodo, InstituicaoFinanceira, TaxaJurosAoMes, TaxaJurosAoAno, cnpj8) de UMA modalidade.
    Devolve lista de dicts (uma por instituição, sem a coluna modalidade), ordem alfabética pelo nome amigável."""
    validos = [r for r in registros if r.get("TaxaJurosAoMes") is not None and FAIXA_AM[0] <= float(r["TaxaJurosAoMes"]) <= FAIXA_AM[1]]
    if not validos:
        return []
    ultimo = max(r["InicioPeriodo"] for r in validos)
    corte = (datetime.date.fromisoformat(ultimo) - datetime.timedelta(days=dias)).isoformat()
    por_inst = {}
    for r in validos:
        if r["InicioPeriodo"] >= corte:
            por_inst.setdefault(r["cnpj8"], []).append(r)
    saida = []
    for cnpj8, lista in por_inst.items():
        if len(lista) < min_janelas:
            continue
        am = statistics.mean(float(x["TaxaJurosAoMes"]) for x in lista)
        aa = statistics.mean(float(x["TaxaJurosAoAno"]) for x in lista)
        saida.append({"cnpj8": cnpj8, "instituicao": nome_amigavel(cnpj8, lista[0]["InstituicaoFinanceira"]), "taxa_am": round(am, 2), "taxa_aa": round(aa, 2),
                      "janelas": len(lista), "periodo_inicio": min(x["InicioPeriodo"] for x in lista), "periodo_fim": max(x["FimPeriodo"] for x in lista)})
    return sorted(saida, key=lambda r: r["instituicao"].lower())


def ler(caminho=CAMINHO_CSV):
    """{chave da modalidade: lista de dicts}. Arquivo ausente -> {}."""
    por_mod = {}
    try:
        with open(caminho, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f, delimiter=";"):
                chave = next((m["chave"] for m in MODALIDADES if m["nome"] == r["modalidade"]), None)
                if chave is None:
                    continue
                por_mod.setdefault(chave, []).append({"cnpj8": r["cnpj8"], "instituicao": r["instituicao"], "taxa_am": float(r["taxa_am"]), "taxa_aa": float(r["taxa_aa"]),
                                                      "janelas": int(r["janelas"]), "periodo_inicio": r["periodo_inicio"], "periodo_fim": r["periodo_fim"]})
    except FileNotFoundError:
        return {}
    return por_mod


def salvar(por_mod, caminho=CAMINHO_CSV):
    """por_mod: {chave: lista de dicts}. Grava na ordem das MODALIDADES e, dentro de cada uma, em ordem alfabética."""
    with open(caminho, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";", lineterminator="\n")
        w.writerow(CABECALHO)
        for m in MODALIDADES:
            for r in sorted(por_mod.get(m["chave"], []), key=lambda x: x["instituicao"].lower()):
                w.writerow([m["nome"], r["cnpj8"], r["instituicao"], "%.2f" % r["taxa_am"], "%.2f" % r["taxa_aa"], r["janelas"], r["periodo_inicio"], r["periodo_fim"]])


def resumo(linhas):
    """Mediana, menor e maior taxa, quantidade e o período coberto."""
    tx = [r["taxa_am"] for r in linhas]
    return {"mediana": statistics.median(tx), "menor": min(tx), "maior": max(tx), "n": len(tx),
            "inicio": min(r["periodo_inicio"] for r in linhas), "fim": max(r["periodo_fim"] for r in linhas)}


def grandes(linhas):
    return [r for r in linhas if r["cnpj8"] in GRANDES]
