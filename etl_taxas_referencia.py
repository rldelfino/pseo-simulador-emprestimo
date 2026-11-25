"""ETL das taxas médias do Banco Central (cheque especial, crédito pessoal não consignado e cartão rotativo).

Lê as séries mensais do SGS (api.bcb.gov.br) e grava os últimos MESES_HISTORICO meses em dados/taxas_referencia.csv.
Idempotente. Falha de rede ou resposta estranha NÃO derruba o pipeline: avisa e sai com código 0, mantendo o CSV que já existe.

Detalhes da API (conferidos ao vivo em 14/11/2026): "ultimos/N" aceita no máximo 20 valores, então pedimos por intervalo de datas
(dataInicial/dataFinal). Os valores vêm como texto com ponto decimal; a data é o primeiro dia do mês de referência.

Uso: python etl_taxas_referencia.py
"""
import datetime
import sys

import requests

import taxas_bancos as tb
import taxas_referencia as tr

MESES_HISTORICO = 24
MINIMO_DE_PONTOS = 12
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; datalab-global-etl/1.0; +https://www.datalabglobal.com)"}


def _inicio_da_janela(hoje, meses):
    total = hoje.year * 12 + (hoje.month - 1) - meses
    return datetime.date(total // 12, total % 12 + 1, 1)


def buscar_serie(codigo, inicio, fim, get=requests.get):
    """Lista [(aaaa-mm, taxa_aa)] da série do SGS entre as datas. Levanta ValueError se a resposta mudou de formato."""
    resp = get("https://api.bcb.gov.br/dados/serie/bcdata.sgs.%d/dados" % codigo,
               params={"formato": "json", "dataInicial": inicio.strftime("%d/%m/%Y"), "dataFinal": fim.strftime("%d/%m/%Y")},
               headers=HEADERS, timeout=30)
    resp.raise_for_status()
    dados = resp.json()
    if not isinstance(dados, list):
        raise ValueError("resposta do SGS mudou de formato (esperava lista): %r" % (str(dados)[:120],))
    pontos = {}
    for item in dados:
        try:
            dia, mes, ano = item["data"].split("/")
            valor = float(str(item["valor"]).replace(",", "."))
        except (KeyError, ValueError, AttributeError):
            continue
        if not (tr.LIMITE_PLAUSIVEL_AA[0] <= valor <= tr.LIMITE_PLAUSIVEL_AA[1]):
            continue
        pontos[ano + "-" + mes] = valor
    return sorted(pontos.items())


def atualizar(caminho=tr.CAMINHO_CSV, hoje=None, get=requests.get):
    """Atualiza o CSV. Devolve {codigo: (qtd_pontos, ultimo_mes)} das séries que foram atualizadas."""
    hoje = hoje or datetime.date.today()
    inicio = _inicio_da_janela(hoje, MESES_HISTORICO)
    existentes = tr.ler(caminho)
    por_serie = {s["codigo"]: [r for r in existentes if r["codigo"] == s["codigo"]] for s in tr.SERIES}
    atualizadas = {}
    for s in tr.SERIES:
        try:
            pontos = buscar_serie(s["codigo"], inicio, hoje, get=get)
        except (requests.RequestException, ValueError) as e:
            print("AVISO taxas BCB: série %d (%s) não atualizada (%s); mantendo o que já existe" % (s["codigo"], s["nome"], e))
            continue
        if len(pontos) < MINIMO_DE_PONTOS:
            print("AVISO taxas BCB: série %d veio com só %d pontos válidos (mínimo %d); mantendo o que já existe" % (s["codigo"], len(pontos), MINIMO_DE_PONTOS))
            continue
        por_serie[s["codigo"]] = [{"codigo": s["codigo"], "modalidade": s["nome"], "mes": m, "taxa_aa": v} for m, v in pontos]
        atualizadas[s["codigo"]] = (len(pontos), pontos[-1][0])
    if atualizadas:
        tr.salvar([r for linhas in por_serie.values() for r in linhas], caminho)
    return atualizadas


def buscar_bancos(modalidade_bcb, get=requests.get):
    """Registros da API de taxas por instituição de UMA modalidade do BCB, mais recentes primeiro. Levanta ValueError se o formato mudou."""
    url = (tb.URL_API + "?$format=json&$top=10000&$orderby=InicioPeriodo%20desc&$filter=Modalidade%20eq%20'"
           + modalidade_bcb.replace(" ", "%20") + "'")
    resp = get(url, headers=HEADERS, timeout=90)
    resp.raise_for_status()
    dados = resp.json()
    if not isinstance(dados, dict) or not isinstance(dados.get("value"), list):
        raise ValueError("resposta do BCB (taxas por instituição) mudou de formato")
    return dados["value"]


def atualizar_bancos(caminho=tb.CAMINHO_CSV, get=requests.get):
    """Atualiza dados/taxas_por_banco.csv. Devolve {chave: (instituições, período_fim)} ou None se manteve o arquivo (falha ou dado pouco confiável)."""
    por_mod = {}
    for m in tb.MODALIDADES:
        try:
            linhas = tb.agregar(buscar_bancos(m["bcb"], get=get))
        except (requests.RequestException, ValueError, KeyError) as e:
            print("AVISO taxas por banco: %s não atualizada (%s); mantendo o arquivo que já existe" % (m["nome"], e))
            return None
        if len(linhas) < tb.MIN_INSTITUICOES:
            print("AVISO taxas por banco: %s com só %d instituições (mínimo %d); mantendo o arquivo que já existe" % (m["nome"], len(linhas), tb.MIN_INSTITUICOES))
            return None
        por_mod[m["chave"]] = linhas
    tb.salvar(por_mod, caminho)
    return {k: (len(v), tb.resumo(v)["fim"]) for k, v in por_mod.items()}


if __name__ == "__main__":
    try:
        resultado = atualizar()
        bancos = atualizar_bancos()
    except OSError as e:
        print("AVISO taxas BCB: não consegui gravar o CSV (%s)" % e)
        sys.exit(0)
    for chave, (n, fim) in sorted((bancos or {}).items()):
        print("OK taxas por banco: %s com %d instituições, período até %s" % (chave, n, fim))
    for codigo, (n, ultimo) in sorted(resultado.items()):
        print("OK taxas BCB: série %d com %d meses, último %s" % (codigo, n, ultimo))
    if not resultado:
        print("AVISO taxas BCB: nenhuma série atualizada; CSV mantido")
    sys.exit(0)
