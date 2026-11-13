"""O site gerado: SEO básico, medição (Umami), CSP, sitemap enxuto e nenhum dado pessoal."""
import datetime
import os
import re

import pytest

import gerador_emprestimo as g

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    pasta = tmp_path_factory.mktemp("site")
    g.gerar_site(str(pasta), hoje=datetime.date(2026, 11, 13))
    return pasta


def ler(site, nome):
    return (site / nome).read_text(encoding="utf-8")


def test_home_tem_seo_basico(site):
    html = ler(site, "index.html")
    assert '<link rel="canonical" href="https://emprestimo.datalabglobal.com/">' in html
    assert 'content="index,follow' in html
    assert "<h1" in html and html.count("<h1") == 1
    assert "Atualizado em 13/11/2026" in html
    assert g.CNPJ in html and g.RAZAO_SOCIAL in html
    assert "análise de crédito" in html


def test_umami_sem_cookies_e_id_certo(site):
    html = ler(site, "index.html")
    assert 'data-website-id="ba3c0b88-59e8-47dd-866d-0b05e5e7dae9"' in html
    assert "https://cloud.umami.is/script.js" in html
    js = ler(site, "simulador.js")
    assert "'cta-pix'" in js and "'usou-simulador-pix'" in js
    assert "adsbygoogle" not in html


def test_csp_libera_umami_e_parceiro_e_nada_a_mais(site):
    cab = ler(site, "_headers")
    assert "https://cloud.umami.is" in cab and "https://gateway.umami.is" in cab
    assert "https://api.triagem.digital" in cab
    assert "frame-ancestors 'none'" in cab
    assert "'unsafe-inline'" not in cab and "'unsafe-eval'" not in cab


def test_html_sem_script_ou_estilo_inline(site):
    html = ler(site, "index.html")
    assert not re.search(r"<script(?![^>]*\bsrc=)[^>]*>", html)
    assert " style=" not in html and "<style" not in html


def test_sitemap_e_robots(site):
    sm = ler(site, "sitemap.xml")
    urls = re.findall(r"<loc>([^<]+)</loc>", sm)
    assert urls and all(u.startswith(g.DOMINIO + "/") for u in urls)
    assert len(urls) <= 30
    assert "404" not in sm
    robots = ler(site, "robots.txt")
    assert "Sitemap: " + g.DOMINIO + "/sitemap.xml" in robots


def test_llms_txt_tem_a_conta_e_o_aviso(site):
    txt = ler(site, "llms.txt")
    assert "0,5479" in txt and "análise de crédito" in txt and g.CNPJ in txt


def test_404_com_noindex(site):
    assert "noindex" in ler(site, "404.html")


def test_calculo_js_embute_a_mesma_tabela(site):
    js = ler(site, "calculo.js")
    assert '"table_uuid": "0IHX41YEUXXD"' in js or '"table_uuid":"0IHX41YEUXXD"' in js
    assert "148.97" in js and "3621.21" in js
    assert "@@" not in js


def test_nenhum_marcador_sobrando(site):
    for nome in ("index.html", "llms.txt", "_headers", "404.html"):
        assert "@@" not in ler(site, nome), nome


def test_sem_cpf_ou_telefone_no_codigo():
    """LGPD: nada de CPF/telefone gravado em arquivos do projeto (fora da cópia de origem)."""
    padroes = [re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"), re.compile(r"\(\d{2}\)\s?9?\d{4}-\d{4}")]
    ignorar = {"origem-hub", "node_modules", "graphify-out", ".git", "__pycache__", ".pytest_cache"}
    for raiz, pastas, arquivos in os.walk(RAIZ):
        pastas[:] = [p for p in pastas if p not in ignorar]
        for a in arquivos:
            if not a.endswith((".py", ".js", ".html", ".json", ".md", ".yml", ".txt", ".xml")):
                continue
            if a == "package-lock.json":
                continue
            texto = open(os.path.join(raiz, a), encoding="utf-8", errors="ignore").read()
            for p in padroes:
                assert not p.search(texto), (a, p.pattern)
