"""Taxas médias de juros do Banco Central usadas só como REFERÊNCIA para comparar o Pix no cartão com outros créditos.

Fonte: BCB/SGS, séries "Taxa média de juros das operações de crédito com recursos livres - Pessoas físicas - ...".
Conferido em 14/11/2026 no catálogo oficial (dadosabertos.bcb.gov.br): unidade "Percentual ao ano", periodicidade mensal,
licença ODbL. Conceito do BCB: taxa média das NOVAS operações de crédito livre contratadas no período, ponderada pelo valor das
concessões. É taxa de juros (não é CET) e é média de mercado: não é oferta nem a taxa que você receberia.

Os dados ficam em dados/taxas_referencia.csv, atualizado por etl_taxas_referencia.py.
"""
import csv
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
CAMINHO_CSV = os.path.join(AQUI, "dados", "taxas_referencia.csv")
CABECALHO = ["codigo_serie", "modalidade", "mes_referencia", "taxa_aa"]

PREFIXO_TITULO = "Taxa média de juros das operações de crédito com recursos livres - Pessoas físicas - "

# códigos conferidos no catálogo oficial do BCB em 14/11/2026
SERIES = [
    dict(codigo=20742, chave="pessoal-nao-consignado", nome="Crédito pessoal não consignado", titulo_bcb=PREFIXO_TITULO + "Crédito pessoal não consignado",
         pagina="20742-taxa-media-de-juros-das-operacoes-de-credito-com-recursos-livres---pessoas-fisicas---credito-"),
    dict(codigo=20741, chave="cheque-especial", nome="Cheque especial", titulo_bcb=PREFIXO_TITULO + "Cheque especial",
         pagina="20741-taxa-media-de-juros-das-operacoes-de-credito-com-recursos-livres---pessoas-fisicas---cheque-e"),
    dict(codigo=22022, chave="cartao-rotativo", nome="Cartão de crédito rotativo", titulo_bcb=PREFIXO_TITULO + "Cartão de crédito rotativo",
         pagina="22022-taxa-media-de-juros-das-operacoes-de-credito-com-recursos-livres---pessoas-fisicas---cartao-d"),
]
LIMITE_PLAUSIVEL_AA = (10.0, 1500.0)  # protege contra série errada: os valores reais ficam entre ~100 e ~500 % ao ano

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]


def url_json(codigo):
    return "https://api.bcb.gov.br/dados/serie/bcdata.sgs.%d/dados?formato=json" % codigo


def url_catalogo(codigo):
    """Página oficial da série no catálogo de dados abertos do BCB (responde 200; o gráfico do www3 estava fora do ar em 14/11/2026)."""
    pagina = next(sr["pagina"] for sr in SERIES if sr["codigo"] == codigo)
    return "https://dadosabertos.bcb.gov.br/dataset/" + pagina


def ler(caminho=CAMINHO_CSV):
    """Lista de dicts {codigo, modalidade, mes, taxa_aa}, ordenada por série e mês. Arquivo ausente -> lista vazia."""
    try:
        with open(caminho, encoding="utf-8", newline="") as f:
            linhas = [{"codigo": int(r["codigo_serie"]), "modalidade": r["modalidade"], "mes": r["mes_referencia"], "taxa_aa": float(r["taxa_aa"])}
                      for r in csv.DictReader(f, delimiter=";")]
    except FileNotFoundError:
        return []
    return sorted(linhas, key=lambda r: (r["codigo"], r["mes"]))


def salvar(linhas, caminho=CAMINHO_CSV):
    linhas = sorted(linhas, key=lambda r: (r["codigo"], r["mes"]))
    with open(caminho, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";", lineterminator="\n")
        w.writerow(CABECALHO)
        for r in linhas:
            w.writerow([r["codigo"], r["modalidade"], r["mes"], "%.2f" % r["taxa_aa"]])


def serie(codigo, linhas=None):
    linhas = ler() if linhas is None else linhas
    return [r for r in linhas if r["codigo"] == codigo]


def ultima(codigo, linhas=None):
    s = serie(codigo, linhas)
    return s[-1] if s else None


def media_ultimos(codigo, n=12, linhas=None):
    s = serie(codigo, linhas)[-n:]
    return sum(r["taxa_aa"] for r in s) / len(s) if s else None


def mensal_equivalente(taxa_aa):
    """Taxa ao mês equivalente (juros compostos) a uma taxa ao ano, em %."""
    return ((1 + taxa_aa / 100) ** (1 / 12) - 1) * 100


def ano_equivalente(taxa_am):
    """Taxa ao ano equivalente (juros compostos) a uma taxa ao mês, em %."""
    return ((1 + taxa_am / 100) ** 12 - 1) * 100


def mes_extenso(ano_mes):
    ano, mes = ano_mes.split("-")
    return MESES[int(mes) - 1] + " de " + ano
