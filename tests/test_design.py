"""Design na mesma família dos outros simuladores: fontes próprias, sem Google Fonts, layout comum e sem estilo inline."""
import datetime
import os
import re

import pytest

import conteudo
import gerador_emprestimo as g
import layout

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTES = ("inter-latin.woff2", "playfair-display-latin.woff2")


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    pasta = tmp_path_factory.mktemp("site_design")
    g.gerar_site(str(pasta), hoje=datetime.date(2026, 11, 14))
    return pasta


def ler(site, nome):
    return (site / nome).read_text(encoding="utf-8")


def paginas():
    return ["index.html"] + [pg["slug"] + ".html" for pg in conteudo.PAGINAS]


def test_fontes_proprias_existem_e_sao_woff2_validos():
    for nome in FONTES:
        caminho = os.path.join(RAIZ, "paginas_seo", "fonts", nome)
        dados = open(caminho, "rb").read()
        assert dados[:4] == b"wOF2" and 20000 < len(dados) < 120000, nome


def test_css_fonte_usa_as_fontes_do_proprio_site():
    css = open(os.path.join(RAIZ, "src", "input.css"), encoding="utf-8").read()
    for nome in FONTES:
        assert "/fonts/" + nome in css
    assert "Playfair Display" in css and "'Inter'" in css
    assert "googleapis" not in css and "gstatic" not in css


def test_nenhuma_pagina_chama_google_fonts_nem_tem_estilo_inline(site):
    for nome in paginas():
        html = ler(site, nome)
        assert "googleapis" not in html and "gstatic" not in html, nome
        assert " style=" not in html and "<style" not in html, nome
    cab = ler(site, "_headers")
    assert "googleapis" not in cab and "gstatic" not in cab
    assert "font-src 'self'" in cab and "/fonts/*" in cab and "immutable" in cab


def test_fontes_pre_carregadas_e_logo_no_cabecalho(site):
    for nome in paginas():
        html = ler(site, nome)
        for f in FONTES:
            assert '<link rel="preload" href="/fonts/' + f + '"' in html, (nome, f)
        assert 'src="/logo-full.png"' in html and 'href="/#simulador"' in html
    assert os.path.exists(os.path.join(RAIZ, "paginas_seo", "logo-full.png"))


def test_rodape_em_colunas_linka_todas_as_paginas(site):
    for nome in paginas():
        html = ler(site, nome)
        rodape = html[html.index("<footer"):]
        for pg in conteudo.PAGINAS:
            assert 'href="/' + pg["slug"] + '"' in rodape, (nome, pg["slug"])
        assert 'href="/feed.xml"' in rodape


def test_menu_do_celular_nativo_sem_javascript(site):
    html = ler(site, "index.html")
    assert '<details class="relative lg:hidden">' in html and "<summary" in html
    for s in g.ENTENDA:
        assert 'href="/' + s + '"' in html[html.index('aria-label="Menu"'):html.index("</header>")]


def test_home_tem_simulador_grafico_e_blocos_do_novo_visual(site):
    html = ler(site, "index.html")
    for i in ("btn-modo-valor", "btn-modo-limite", "campo-valor", "range-valor", "range-parcelas", "r-pix", "r-total", "r-iof", "r-cet", "r-juros",
              "donut", "barras", "txt-barras", "cta-pix", "aviso-celular", "aviso-minimo", "leg-pix", "leg-custo"):
        assert 'id="' + i + '"' in html, i
    assert html.count("<h1") == 1
    assert "glass-panel" in html and "glass-panel-emerald" in html and "bg-gradient-to-br" in html
    assert "violet" not in html  # a paleta agora é a esmeralda da família


def test_guias_com_cabecalho_em_selo_e_painel(site):
    for pg in conteudo.PAGINAS:
        html = ler(site, pg["slug"] + ".html")
        assert 'class="mx-auto max-w-3xl pb-4"' in html and "glass-panel" in html, pg["slug"]
        assert html.count("<h1") == 1


def test_textos_das_paginas_nao_usam_a_cor_antiga():
    for classe in (conteudo.C_A, conteudo.C_AVISO, conteudo.C_TH, conteudo.C_TD, conteudo.C_H2):
        assert "violet" not in classe
    assert "violet" not in layout.HOME_MAIN and "violet" not in layout.LAYOUT


def test_simulador_js_sem_innerhtml_e_com_rosca_e_barras():
    js = open(os.path.join(RAIZ, "src", "simulador.js"), encoding="utf-8").read()
    assert ".innerHTML" not in js and "insertAdjacentHTML" not in js  # só textContent e atributos SVG
    assert "desenharRosca" in js and "desenharBarras" in js
    assert "w-0 min-w-0 flex-1" in js  # regressão: as barras estouravam a largura em 320 px


def test_css_tem_versao_no_endereco_e_bate_com_o_arquivo(site):
    """styles.css tem cache imutável de 1 ano: sem a versão no endereço, quem já visitou ficaria com o CSS velho."""
    import hashlib
    caminho = os.path.join(RAIZ, "paginas_seo", "styles.css")
    esperado = hashlib.sha256(open(caminho, "rb").read()).hexdigest()[:10]
    assert g.versao_css() == esperado
    for nome in paginas() + ["404.html"]:
        html = ler(site, nome)
        assert 'href="/styles.css?v=' + esperado + '"' in html, nome
        assert 'href="/styles.css"' not in html, nome
