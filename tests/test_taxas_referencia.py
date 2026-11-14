"""Taxas médias do Banco Central: ETL (sem rede), dados gravados e a página de referência."""
import datetime
import re

import pytest
import requests

import calculo
import conteudo
import etl_taxas_referencia as etl
import gerador_emprestimo as g
import taxas_referencia as tr


class RespostaFalsa:
    def __init__(self, dados, status=200):
        self._dados, self.status_code = dados, status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError("HTTP %d" % self.status_code)

    def json(self):
        return self._dados


def serie_falsa(n=20, inicio=(2025, 2), base=100.0):
    saida = []
    ano, mes = inicio
    for i in range(n):
        saida.append({"data": "01/%02d/%d" % (mes, ano), "valor": "%.2f" % (base + i)})
        mes += 1
        if mes == 13:
            mes, ano = 1, ano + 1
    return saida


def test_codigos_das_series_confirmados_no_catalogo_do_bcb():
    assert {s["codigo"]: s["nome"] for s in tr.SERIES} == {
        20742: "Crédito pessoal não consignado", 20741: "Cheque especial", 22022: "Cartão de crédito rotativo"}
    for s in tr.SERIES:
        assert s["titulo_bcb"].startswith("Taxa média de juros das operações de crédito com recursos livres - Pessoas físicas - ")
        assert "bcdata.sgs.%d" % s["codigo"] in tr.url_json(s["codigo"])
        assert "hdOidSeriesSelecionadas=%d" % s["codigo"] in tr.url_grafico(s["codigo"])


def test_dados_gravados_estao_completos_e_plausiveis():
    linhas = tr.ler()
    assert linhas
    ultimos = set()
    for s in tr.SERIES:
        pontos = tr.serie(s["codigo"], linhas)
        assert len(pontos) >= etl.MINIMO_DE_PONTOS
        meses = [p["mes"] for p in pontos]
        assert meses == sorted(set(meses)), "meses repetidos ou fora de ordem"
        assert all(re.fullmatch(r"\d{4}-\d{2}", m) for m in meses)
        assert all(tr.LIMITE_PLAUSIVEL_AA[0] <= p["taxa_aa"] <= tr.LIMITE_PLAUSIVEL_AA[1] for p in pontos)
        ultimos.add(meses[-1])
    # o BCB pode publicar uma série antes da outra: aceitamos até 1 mês de diferença entre as três
    nums = sorted(int(m[:4]) * 12 + int(m[5:]) for m in ultimos)
    assert nums[-1] - nums[0] <= 1, ultimos


def test_ordem_de_grandeza_das_series():
    u = {s["chave"]: tr.ultima(s["codigo"])["taxa_aa"] for s in tr.SERIES}
    assert u["pessoal-nao-consignado"] < u["cheque-especial"] < u["cartao-rotativo"]


def test_equivalencias_de_taxa():
    assert tr.mensal_equivalente(tr.ano_equivalente(7.49)) == pytest.approx(7.49)
    # a API do parceiro devolveu interestAnnual = 137,93 para 12x (13/11/2026)
    assert tr.ano_equivalente(calculo.simular("valor", 1000, 0, 12)["jurosMes"]) == pytest.approx(137.93, abs=0.05)
    assert tr.mes_extenso("2026-09") == "setembro de 2026"


def test_etl_pede_por_intervalo_de_datas_e_grava(tmp_path):
    chamadas = []

    def get(url, params=None, headers=None, timeout=None):
        chamadas.append((url, params))
        return RespostaFalsa(serie_falsa())

    caminho = str(tmp_path / "taxas.csv")
    res = etl.atualizar(caminho=caminho, hoje=datetime.date(2026, 11, 14), get=get)
    assert set(res) == {s["codigo"] for s in tr.SERIES}
    assert all(n == 20 for n, _ in res.values())
    assert all("dataInicial" in p and "dataFinal" in p and "ultimos" not in u for u, p in chamadas)
    assert chamadas[0][1]["dataInicial"] == "01/11/2024"
    assert len(tr.ler(caminho)) == 20 * len(tr.SERIES)


def test_etl_e_idempotente(tmp_path):
    caminho = str(tmp_path / "taxas.csv")
    get = lambda url, params=None, headers=None, timeout=None: RespostaFalsa(serie_falsa())
    etl.atualizar(caminho=caminho, hoje=datetime.date(2026, 11, 14), get=get)
    primeiro = open(caminho, encoding="utf-8").read()
    etl.atualizar(caminho=caminho, hoje=datetime.date(2026, 11, 14), get=get)
    assert open(caminho, encoding="utf-8").read() == primeiro


def test_etl_falha_de_rede_mantem_o_arquivo(tmp_path):
    caminho = str(tmp_path / "taxas.csv")
    etl.atualizar(caminho=caminho, hoje=datetime.date(2026, 11, 14), get=lambda *a, **k: RespostaFalsa(serie_falsa()))
    antes = open(caminho, encoding="utf-8").read()

    def cai(*a, **k):
        raise requests.ConnectionError("sem rede")

    assert etl.atualizar(caminho=caminho, hoje=datetime.date(2026, 11, 14), get=cai) == {}
    assert open(caminho, encoding="utf-8").read() == antes


@pytest.mark.parametrize("resposta", [{"erro": {"statusCode": 400}}, [], serie_falsa(5)])
def test_etl_rejeita_resposta_estranha_ou_curta(tmp_path, resposta):
    caminho = str(tmp_path / "taxas.csv")
    assert etl.atualizar(caminho=caminho, hoje=datetime.date(2026, 11, 14), get=lambda *a, **k: RespostaFalsa(resposta)) == {}
    assert tr.ler(caminho) == []


def test_etl_descarta_valor_fora_da_faixa_e_aceita_virgula():
    dados = serie_falsa(14) + [{"data": "01/04/2026", "valor": "9999"}, {"data": "01/05/2026", "valor": "abc"}, {"data": "lixo", "valor": "1"}]
    dados[0]["valor"] = "123,45"
    pontos = dict(etl.buscar_serie(20741, datetime.date(2025, 1, 1), datetime.date(2026, 11, 14), get=lambda *a, **k: RespostaFalsa(dados)))
    assert pontos["2025-02"] == 123.45
    assert "2026-04" not in pontos or pontos["2026-04"] != 9999


def test_etl_nao_derruba_se_http_der_erro(tmp_path):
    caminho = str(tmp_path / "taxas.csv")
    assert etl.atualizar(caminho=caminho, hoje=datetime.date(2026, 11, 14), get=lambda *a, **k: RespostaFalsa({}, status=502)) == {}


# ---------- página ----------

@pytest.fixture(scope="module")
def site(tmp_path_factory):
    pasta = tmp_path_factory.mktemp("site4")
    g.gerar_site(str(pasta), hoje=datetime.date(2026, 11, 14))
    return pasta


def texto(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html).replace("&quot;", '"')).strip()


def test_pagina_de_taxas_tem_numero_data_e_link_de_cada_serie(site):
    html = (site / "taxas-de-referencia.html").read_text(encoding="utf-8")
    t = texto(html)
    for s in tr.SERIES:
        u = tr.ultima(s["codigo"])
        assert conteudo.pct(u["taxa_aa"]) in t, s["nome"]
        assert tr.mes_extenso(u["mes"]) in t
        assert tr.url_json(s["codigo"]) in html and tr.url_grafico(s["codigo"]) in html
    assert "ODbL" in t and "percentual ao ano" in t.lower()
    assert "É juros, não é CET" in t
    assert t.count("Pix no cartão") >= 3


def test_pagina_de_taxas_compara_com_o_pix_e_diz_quando_ha_opcao_mais_barata(site):
    t = texto((site / "taxas-de-referencia.html").read_text(encoding="utf-8"))
    pix12 = tr.ano_equivalente(calculo.simular("valor", 1000, 0, 12)["jurosMes"])
    assert conteudo.pct(pix12) in t
    ultimas = {s["chave"]: tr.ultima(s["codigo"])["taxa_aa"] for s in tr.SERIES}
    if ultimas["pessoal-nao-consignado"] < pix12 * 0.97:
        assert "tem juros menores que o Pix no cartão em 12x" in t
    assert "não garante que você consiga essa taxa" in t or "nenhuma das três" in t


def test_outras_paginas_usam_os_mesmos_numeros(site):
    comparar = texto((site / "pix-no-cartao-ou-outro-credito.html").read_text(encoding="utf-8"))
    home = texto((site / "index.html").read_text(encoding="utf-8"))
    pessoal = tr.ultima(20742)
    assert conteudo.pct(pessoal["taxa_aa"]) in comparar and conteudo.pct(pessoal["taxa_aa"]) in home
    assert "Ainda não mostramos" not in comparar
    metodologia = texto((site / "metodologia.html").read_text(encoding="utf-8"))
    for codigo in ("20742", "20741", "22022"):
        assert codigo in metodologia


def test_pagina_de_taxas_esta_no_sitemap_e_no_menu(site):
    assert g.DOMINIO + "/taxas-de-referencia" in (site / "sitemap.xml").read_text(encoding="utf-8")
    assert 'href="/taxas-de-referencia"' in (site / "index.html").read_text(encoding="utf-8")
