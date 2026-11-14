"""Fase 5: IndexNow, dados abertos (licenças certas), feed Atom e pacote de publicação."""
import datetime
import io
import json
import os
import re
import urllib.error
import xml.etree.ElementTree as ET

import pytest

import calculo
import conteudo
import dados_abertos as da
import feed_atom
import gerador_emprestimo as g
import indexnow
import publicacao
import taxas_referencia as tr


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    pasta = tmp_path_factory.mktemp("site5")
    g.gerar_site(str(pasta), hoje=datetime.date(2026, 11, 14))
    return pasta


def ler(site, nome):
    return (site / nome).read_text(encoding="utf-8")


# ---------- IndexNow ----------

class Resp:
    def __init__(self, corpo, status=200):
        self.status, self._c = status, corpo.encode("utf-8")

    def read(self):
        return self._c

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_chave_indexnow_publicada_e_igual(site):
    assert re.fullmatch(r"[0-9a-f]{32}", indexnow.CHAVE)
    assert ler(site, indexnow.CHAVE + ".txt").strip() == indexnow.CHAVE
    assert indexnow.LOCAL_DA_CHAVE == "https://emprestimo.datalabglobal.com/" + indexnow.CHAVE + ".txt"


def test_payload_so_com_urls_do_proprio_site(site):
    urls = indexnow.urls_do_sitemap(str(site / "sitemap.xml"))
    assert len(urls) == len(g.PAGINAS_INDEXAVEIS) and all(u.startswith("https://emprestimo.datalabglobal.com/") for u in urls)
    payload = indexnow.montar_payload(urls)
    assert payload["host"] == "emprestimo.datalabglobal.com" and payload["key"] == indexnow.CHAVE
    assert payload["keyLocation"] == indexnow.LOCAL_DA_CHAVE and payload["urlList"] == urls


def test_nao_envia_se_o_site_nao_esta_no_ar(site):
    enviados = []

    def cai(*a, **k):
        raise urllib.error.URLError("sem site")

    assert indexnow.main(str(site / "sitemap.xml"), abrir=cai, enviar_fn=enviados.append) == 0
    assert enviados == []
    # chave com conteúdo diferente também conta como "não está no ar"
    assert indexnow.main(str(site / "sitemap.xml"), abrir=lambda *a, **k: Resp("outra-coisa"), enviar_fn=enviados.append) == 0
    assert enviados == []


def test_envia_quando_no_ar_e_espera_o_deploy(site):
    enviados, esperas = [], []
    codigo = indexnow.main(str(site / "sitemap.xml"), espera=240, abrir=lambda *a, **k: Resp(indexnow.CHAVE),
                           enviar_fn=lambda payload: enviados.append(payload) or 200, dormir=esperas.append)
    assert codigo == 0 and esperas == [240] and len(enviados) == 1
    assert enviados[0]["key"] == indexnow.CHAVE


def test_erro_http_do_indexnow_nao_derruba(site, capsys):
    def erro(payload):
        raise urllib.error.HTTPError("u", 422, "Unprocessable", {}, io.BytesIO(b""))

    assert indexnow.main(str(site / "sitemap.xml"), abrir=lambda *a, **k: Resp(indexnow.CHAVE), enviar_fn=erro) == 0
    assert "HTTP 422" in capsys.readouterr().out


# ---------- dados abertos ----------

def test_tabela_10_aberta_bate_com_a_conta(site):
    linhas = list(__import__("csv").DictReader(io.StringIO(ler(site, "dados/pix-no-cartao-tabela-10.csv"))))
    assert [int(l["parcelas"]) for l in linhas] == calculo.PARCELAS
    d12 = next(l for l in linhas if l["parcelas"] == "12")
    assert (d12["parcela_por_r1000"], d12["total_por_r1000"], d12["iof_por_r1000"], d12["cet_aa_pct"]) == ("131.99", "1583.90", "33.32", "148.97")
    assert d12["juros_aa_equivalente_pct"] == "137.91"
    for l in linhas:
        n = int(l["parcelas"])
        assert float(l["total_por_r1000"]) == pytest.approx(1000 * (1 + float(l["fator_total"])), abs=0.01)
        assert float(l["parcela_por_r1000"]) == pytest.approx(float(l["total_por_r1000"]) / n, abs=0.01)


def test_series_do_bcb_abertas_batem_com_o_csv_interno(site):
    linhas = list(__import__("csv").DictReader(io.StringIO(ler(site, "dados/taxas-referencia-bcb.csv"))))
    assert len(linhas) == len(tr.ler())
    assert {int(l["codigo_serie"]) for l in linhas} == {20741, 20742, 22022}
    for l in linhas:
        assert float(l["taxa_am_equivalente_pct"]) == pytest.approx(tr.mensal_equivalente(float(l["taxa_aa_pct"])), abs=0.01)
        assert l["fonte_url"].startswith("https://api.bcb.gov.br/dados/serie/bcdata.sgs.")


def test_licencas_cada_conjunto_com_a_da_sua_fonte(site):
    pix = json.loads(ler(site, "dados/datapackage-pix-no-cartao-tabela-10.json"))
    bcb = json.loads(ler(site, "dados/datapackage-taxas-referencia-bcb.json"))
    assert pix["licenses"][0]["name"] == "CC-BY-4.0"
    assert bcb["licenses"][0]["name"] == "ODbL-1.0"  # o BCB publica sob ODbL: base derivada segue a mesma licença
    assert "Banco Central" in da.texto_licenca(da.BCB) and "ODbL 1.0" in da.texto_licenca(da.BCB)
    assert "CC BY 4.0" in da.texto_licenca(da.PIX)
    assert "CC BY" not in da.texto_licenca(da.BCB).replace("não é CC BY", "")
    for pacote in (pix, bcb):
        assert pacote["resources"][0]["schema"]["fields"] and pacote["sources"]
    assert bcb["temporal"]["end"] == max(r["mes"] for r in tr.ler())


def test_pagina_de_dados_abertos(site):
    html = ler(site, "dados-abertos.html")
    t = re.sub(r"<[^>]+>", " ", html)
    assert "CC BY 4.0" in t and "ODbL 1.0" in t and "Contém informações do Banco Central" in t
    assert "Como citar" in t and "Datalab Global (https://emprestimo.datalabglobal.com/dados-abertos)" in t
    for c in da.CONJUNTOS:
        for arq in (c["nome"] + ".csv", c["nome"] + ".json", "datapackage-" + c["nome"] + ".json"):
            assert 'href="/dados/' + arq + '"' in html
            assert (site / "dados" / arq).exists()
    assert g.DOMINIO + "/dados-abertos" in ler(site, "sitemap.xml")
    assert 'href="/dados-abertos"' in ler(site, "index.html")  # rodapé


# ---------- feed Atom ----------

def test_feed_atom_valido_e_com_ids_unicos(site):
    ns = {"a": "http://www.w3.org/2005/Atom"}
    raiz = ET.fromstring(ler(site, "feed.xml").encode("utf-8"))
    entradas = raiz.findall("a:entry", ns)
    ids = [e.find("a:id", ns).text for e in entradas]
    assert len(ids) == len(set(ids)) and len(entradas) >= len(conteudo.ATUALIZACOES) + 3
    for e in entradas:
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T00:00:00Z", e.find("a:updated", ns).text)
        assert e.find("a:link", ns).get("href").startswith("https://emprestimo.datalabglobal.com/")
    datas = [e.find("a:updated", ns).text for e in entradas]
    assert datas == sorted(datas, reverse=True)
    assert raiz.find("a:updated", ns).text >= datas[0]
    assert any("Taxas médias do Banco Central de" in e.find("a:title", ns).text for e in entradas)


def test_feed_anunciado_no_head_e_no_llms(site):
    assert '<link rel="alternate" type="application/atom+xml"' in ler(site, "index.html")
    llms = ler(site, "llms.txt")
    assert "/feed.xml" in llms and "dados-abertos" in llms


# ---------- publicação ----------

def test_pacote_de_publicacao_sem_segredos(site, tmp_path):
    saida = tmp_path / "publicacao"
    resumo = publicacao.gerar(str(site / "dados"), str(saida))
    assert resumo == {"pix-no-cartao-tabela-10": 11, "taxas-referencia-bcb": len(tr.ler())}
    for nome, lic in (("pix-no-cartao-tabela-10", "CC-BY-4.0"), ("taxas-referencia-bcb", "ODbL-1.0")):
        meta = json.loads((saida / "kaggle" / nome / "dataset-metadata.json").read_text(encoding="utf-8"))
        assert meta["licenses"] == [{"name": lic}] and meta["id"].startswith("SEU_USUARIO_KAGGLE/")
        assert (saida / "kaggle" / nome / (nome + ".csv")).exists() and (saida / "huggingface" / nome / (nome + ".csv")).exists()
        card = (saida / "huggingface" / nome / "README.md").read_text(encoding="utf-8")
        assert card.startswith("---\nlicense: " + ("cc-by-4.0" if lic == "CC-BY-4.0" else "odbl"))
    gov = (saida / "dados-gov-br" / "cadastro.md").read_text(encoding="utf-8")
    assert "/dados/pix-no-cartao-tabela-10.csv" in gov and "/dados/taxas-referencia-bcb.csv" in gov
    todos = "".join(open(os.path.join(r, f), encoding="utf-8", errors="ignore").read() for r, _d, fs in os.walk(saida) for f in fs if f.endswith((".json", ".md")))
    assert not re.search(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*\S{8,}", todos)
    assert "KAGGLE_KEY" in (saida / "LEIA-ME.md").read_text(encoding="utf-8")  # só o nome da variável, nunca o valor


def test_textos_quebram_linha_para_enderecos_longos_no_celular():
    # regressão: o endereço longo da licença estourava a largura em 375 px
    for classe in (conteudo.C_P, conteudo.C_UL, conteudo.C_OL, conteudo.C_AVISO):
        assert "break-words" in classe
