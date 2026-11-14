"""Dados abertos do simulador: gera os arquivos em paginas_seo/dados/ a partir das mesmas fontes do site.

Dois conjuntos, cada um com a licença que a fonte permite:
1. pix-no-cartao-tabela-10: a conta e as taxas da Tabela 10 do parceiro. Licença CC BY 4.0.
2. taxas-referencia-bcb: as séries do Banco Central (SGS 20742, 20741, 22022). O BCB publica essas séries sob ODbL 1.0 (conferido no catálogo de
   dados abertos em 14/11/2026), que exige que bases derivadas sigam a mesma licença. Por isso este conjunto é ODbL 1.0, não CC BY.
"""
import csv
import io
import json
import os

import calculo
import taxas_referencia as tr

DOMINIO = "https://emprestimo.datalabglobal.com"
CITACAO = "Datalab Global (https://emprestimo.datalabglobal.com/dados-abertos)"

CC_BY = {"id": "CC-BY-4.0", "titulo": "CC BY 4.0", "url": "https://creativecommons.org/licenses/by/4.0/deed.pt-br"}
ODBL = {"id": "ODbL-1.0", "titulo": "ODbL 1.0", "url": "https://opendatacommons.org/licenses/odbl/1-0/"}

PIX = dict(
    nome="pix-no-cartao-tabela-10",
    titulo="Pix no cartão de crédito: Tabela 10 do parceiro (parcela, IOF, juros e CET)",
    descricao=("Condições do Pix no cartão de crédito segundo a Tabela 10 do parceiro (correspondente bancário), de 2 a 12 parcelas, para cada R$ 1.000 recebidos por Pix: "
               "fator total, parcela, total na fatura, IOF, juros ao mês, juros equivalentes ao ano e CET ao ano. Valor do Pix de R$ 300 a R$ 5.000. "
               "Os números são conferidos toda semana contra a API do próprio parceiro."),
    licenca=CC_BY,
    fonte=dict(title="Parceiro do Pix no cartão (correspondente bancário) — Tabela 10, conferida pela API de simulação", path=DOMINIO + "/metodologia"),
    colunas=[
        ("parcelas", "integer", "Número de parcelas na fatura (2 a 12)"),
        ("juros_am_pct", "number", "Juros ao mês, % (tabelado pelo parceiro)"),
        ("juros_aa_equivalente_pct", "number", "Juros ao ano equivalentes (juros compostos sobre a taxa mensal), %"),
        ("cet_aa_pct", "number", "Custo efetivo total ao ano, % (tabelado pelo parceiro)"),
        ("fator_total", "number", "Fator da Tabela 10: 0,5479 + 0,003 x parcelas. Total na fatura = valor no Pix x (1 + fator)"),
        ("parcela_por_r1000", "number", "Valor de cada parcela, em R$, para receber R$ 1.000"),
        ("total_por_r1000", "number", "Total na fatura, em R$, para receber R$ 1.000"),
        ("iof_por_r1000", "number", "IOF (já incluso no total), em R$, para receber R$ 1.000"),
    ],
)

BCB = dict(
    nome="taxas-referencia-bcb",
    titulo="Taxas médias de juros do Banco Central: cheque especial, crédito pessoal não consignado e cartão rotativo",
    descricao=("Taxa média de juros das novas operações de crédito com recursos livres, pessoas físicas, ponderada pelo valor das concessões, em % ao ano, série mensal, "
               "para cheque especial (SGS 20741), crédito pessoal não consignado (SGS 20742) e cartão de crédito rotativo (SGS 22022). "
               "Inclui a taxa ao mês equivalente, calculada por juros compostos."),
    licenca=ODBL,
    fonte=dict(title="Banco Central do Brasil — SGS (dados abertos, ODbL)", path="https://dadosabertos.bcb.gov.br/"),
    colunas=[
        ("codigo_serie", "integer", "Código da série no SGS do Banco Central"),
        ("modalidade", "string", "Modalidade de crédito"),
        ("mes_referencia", "string", "Mês de referência (AAAA-MM)"),
        ("taxa_aa_pct", "number", "Taxa média de juros, % ao ano (dado do Banco Central)"),
        ("taxa_am_equivalente_pct", "number", "Taxa ao mês equivalente, % (cálculo da Datalab Global)"),
        ("fonte_url", "string", "Endereço da série no SGS (JSON)"),
    ],
)

CONJUNTOS = [PIX, BCB]


def linhas_pix():
    t = calculo.TABELA
    saida = []
    for n in calculo.PARCELAS:
        r = calculo.simular("valor", 1000, 0, n)
        saida.append({
            "parcelas": n,
            "juros_am_pct": "%.2f" % r["jurosMes"],
            "juros_aa_equivalente_pct": "%.2f" % tr.ano_equivalente(r["jurosMes"]),
            "cet_aa_pct": "%.2f" % r["cetAno"],
            "fator_total": "%.4f" % (t["fator_base"] + t["fator_por_parcela"] * n),
            "parcela_por_r1000": "%.2f" % r["parcela"],
            "total_por_r1000": "%.2f" % r["total"],
            "iof_por_r1000": "%.2f" % r["iof"],
        })
    return saida


def linhas_bcb():
    saida = []
    for r in tr.ler():
        saida.append({
            "codigo_serie": r["codigo"], "modalidade": r["modalidade"], "mes_referencia": r["mes"],
            "taxa_aa_pct": "%.2f" % r["taxa_aa"], "taxa_am_equivalente_pct": "%.2f" % tr.mensal_equivalente(r["taxa_aa"]),
            "fonte_url": tr.url_json(r["codigo"]),
        })
    return saida


LINHAS = {PIX["nome"]: linhas_pix, BCB["nome"]: linhas_bcb}


def csv_texto(conjunto, linhas):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    cols = [c[0] for c in conjunto["colunas"]]
    w.writerow(cols)
    for l in linhas:
        w.writerow([l[c] for c in cols])
    return buf.getvalue()


def datapackage(conjunto, linhas):
    tipos = {"integer": "integer", "number": "number", "string": "string"}
    lic = conjunto["licenca"]
    pacote = {
        "name": conjunto["nome"],
        "title": conjunto["titulo"],
        "description": conjunto["descricao"],
        "licenses": [{"name": lic["id"], "path": lic["url"], "title": lic["titulo"]}],
        "sources": [conjunto["fonte"]],
        "contributors": [{"title": "Datalab Global", "role": "publisher", "path": DOMINIO + "/"}],
        "resources": [{
            "name": "dados", "path": conjunto["nome"] + ".csv", "format": "csv", "mediatype": "text/csv", "encoding": "utf-8",
            "schema": {"fields": [{"name": n, "type": tipos[t], "description": d} for n, t, d in conjunto["colunas"]]},
        }],
        "keywords": ["crédito", "juros", "Brasil"],
    }
    if conjunto is BCB:
        meses = sorted({l["mes_referencia"] for l in linhas})
        pacote["temporal"] = {"start": meses[0], "end": meses[-1]}
    return pacote


def texto_licenca(conjunto):
    lic = conjunto["licenca"]
    if conjunto is BCB:
        return ("Contém informações do Banco Central do Brasil, disponibilizadas por ele sob a licença ODbL 1.0 (" + ODBL["url"] + "). "
                "Esta base derivada também é licenciada sob ODbL 1.0: você pode copiar, distribuir e adaptar, citando a fonte e mantendo a mesma licença.")
    return "Licença " + lic["titulo"] + " (" + lic["url"] + "): você pode copiar, distribuir e adaptar, citando " + CITACAO + "."


def readme(linhas_por_nome):
    partes = ["# Dados abertos: Pix no cartão (Datalab Global)\n",
              "Gerado automaticamente pelo simulador em " + DOMINIO + ". Cada conjunto tem a licença que a sua fonte permite.\n"]
    for c in CONJUNTOS:
        partes.append("\n## " + c["titulo"] + "\n\n" + c["descricao"] + "\n\n- Arquivos: `" + c["nome"] + ".csv`, `" + c["nome"] + ".json`, `datapackage-" + c["nome"] + ".json`")
        partes.append("- " + texto_licenca(c))
        partes.append("- Como citar: " + CITACAO + ".")
        partes.append("- Linhas: " + str(len(linhas_por_nome[c["nome"]])) + "\n\nColunas:\n")
        partes.extend("- `" + n + "` (" + t + "): " + d for n, t, d in c["colunas"])
    partes.append("\nLimites: as taxas do Banco Central são médias de mercado, não ofertas. A Tabela 10 é do parceiro e pode mudar; a conferência é semanal.\n")
    return "\n".join(partes)


def gerar(pasta_dados):
    """Escreve os arquivos em pasta_dados e devolve {nome: linhas}."""
    os.makedirs(pasta_dados, exist_ok=True)
    por_nome = {}
    for c in CONJUNTOS:
        linhas = LINHAS[c["nome"]]()
        por_nome[c["nome"]] = linhas
        _gravar(os.path.join(pasta_dados, c["nome"] + ".csv"), csv_texto(c, linhas))
        _gravar(os.path.join(pasta_dados, c["nome"] + ".json"), json.dumps(linhas, ensure_ascii=False, indent=1) + "\n")
        _gravar(os.path.join(pasta_dados, "datapackage-" + c["nome"] + ".json"), json.dumps(datapackage(c, linhas), ensure_ascii=False, indent=1) + "\n")
    _gravar(os.path.join(pasta_dados, "README.md"), readme(por_nome))
    return por_nome


def _gravar(caminho, texto):
    with open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)
