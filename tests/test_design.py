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
        assert 'src="/logo-full.png?v=' + g.versao_icones() + '"' in html and 'href="/#simulador"' in html
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
    assert "glass-panel" in html and "glass-panel-violet" in html and "bg-gradient-to-br" in html
    assert "emerald" not in html and "violet" in html  # a paleta do Pix no cartão é a roxa (verde é do imobiliário, azul dos veículos)


def test_guias_com_cabecalho_em_selo_e_painel(site):
    for pg in conteudo.PAGINAS:
        html = ler(site, pg["slug"] + ".html")
        assert 'class="mx-auto max-w-3xl pb-4"' in html and "glass-panel" in html, pg["slug"]
        assert html.count("<h1") == 1


def test_paleta_e_roxa_e_nao_usa_o_verde_do_imobiliario_nem_o_azul_dos_veiculos():
    for classe in (conteudo.C_A, conteudo.C_TH):
        assert "violet" in classe and "emerald" not in classe
    for texto in (layout.HOME_MAIN, layout.LAYOUT, layout.GUIA_FECHO, layout.GUIA_CABECALHO, layout.GUIA_MEIO):
        assert "emerald" not in texto and "teal" not in texto and "green" not in texto
    css = open(os.path.join(RAIZ, "src", "input.css"), encoding="utf-8").read()
    js = open(os.path.join(RAIZ, "src", "simulador.js"), encoding="utf-8").read()
    for fonte in (css, js):
        assert "#10b981" not in fonte and "#34d399" not in fonte and "16, 185, 129" not in fonte
    assert "#8b5cf6" in js and "#a78bfa" in css


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


def test_scripts_tem_versao_no_endereco_e_bate_com_o_conteudo(site):
    """O Cloudflare guarda .js na borda por horas: sem ?v=, o HTML novo podia receber o JS antigo (aconteceu no deploy do redesign)."""
    html = ler(site, "index.html")
    assert 'src="/calculo.js?v=' + g.versao_calculo_js() + '"' in html
    assert 'src="/simulador.js?v=' + g.versao_simulador_js() + '"' in html
    assert 'src="/simulador.js"' not in html and 'src="/calculo.js"' not in html
    assert g.versao_simulador_js() != g.versao_calculo_js()
    # o conteúdo servido é o do src (o gerador copia o arquivo sem alterar)
    assert (site / "simulador.js").read_bytes() == open(os.path.join(RAIZ, "src", "simulador.js"), "rb").read()


# --- revisão geral de 16/11/2026 -------------------------------------------------------------

def test_menu_js_com_versao_em_todas_as_paginas_e_conteudo_igual_ao_src(site):
    for nome in paginas():
        assert 'src="/menu.js?v=' + g.versao_menu_js() + '"' in ler(site, nome), nome
    assert (site / "menu.js").read_bytes() == open(os.path.join(RAIZ, "src", "menu.js"), "rb").read()
    assert "/menu.js" in ler(site, "_headers")


def test_cartao_do_twitter_e_security_txt(site):
    for nome in paginas():
        html = ler(site, nome)
        assert 'name="twitter:card" content="summary_large_image"' in html, nome
        assert 'name="twitter:image" content="' + g.DOMINIO + '/og-image.png?v=' + g.versao_og_image() + '"' in html, nome
        assert 'property="og:image" content="' + g.DOMINIO + '/og-image.png?v=' + g.versao_og_image() + '"' in html, nome
    sec = ler(site, ".well-known/security.txt")
    assert "Contact: mailto:" + g.EMAIL in sec and "Expires: 2027-11-14T" in sec


def test_home_nao_chama_juros_ao_mes_de_cet():
    assert "O CET vai de 34,64% ao mês" not in layout.HOME_MAIN
    assert "Os juros vão de 34,64% ao mês" in layout.HOME_MAIN


def test_titulos_cabem_no_resultado_do_google():
    for pg in conteudo.PAGINAS:
        assert len(pg["title"]) <= 60, (pg["slug"], len(pg["title"]))


def test_abas_com_painel_campo_de_texto_barra_fixa_e_aviso_da_proposta(site):
    html = ler(site, "index.html")
    assert html.count('aria-controls="painel-simulacao"') == 2 and 'id="painel-simulacao" role="tabpanel"' in html
    assert 'id="campo-valor" type="text" inputmode="decimal"' in html
    for i in ("barra-resumo", "btn-resumo", "resultado", "aviso-proposta", "txt-aviso-proposta", "link-parceiro"):
        assert 'id="' + i + '"' in html, i
    assert html.count("<div") == html.count("</div>")  # o painel novo não deixou tag aberta


def test_modo_limite_aceita_a_partir_do_minimo_e_avisa_quando_falta_limite():
    js = open(os.path.join(RAIZ, "src", "simulador.js"), encoding="utf-8").read()
    assert "var LIMITE_MIN = 300;" in js and "limiteNecessario" in js
    assert "aria-valuetext" in js and "ArrowRight" in js and "IntersectionObserver" in js
    assert "cta-pix-sem-preenchimento" in js  # não segue calado quando o parceiro não responde


def test_links_de_destaque_e_404_com_area_de_toque(site):
    html = ler(site, "index.html")
    assert 'inline-flex min-h-11 items-center font-semibold text-violet-300 underline hover:text-white" href="/custo-cet-iof"' in html
    assert "min-h-11" in ler(site, "404.html")


def test_resultado_compara_com_o_bcb_avisa_do_pedido_real_e_copia_o_link(site):
    html = ler(site, "index.html")
    for i in ("referencia", "ref-lista", "ref-veredito", "ref-nota", "aviso-pedido", "btn-copiar", "msg-copiado",
              "detalhe-prazos", "corpo-prazos", "cap-prazos"):
        assert 'id="' + i + '"' in html, i
    # o aviso do pedido real vem ANTES do botão que abre o parceiro, e o texto do botão não mudou
    assert html.index('id="aviso-pedido"') < html.index('id="cta-pix"')
    assert "6 passos, com CPF e documento original" in html and "Ver minha proposta" in html
    assert html.count("<div") == html.count("</div>") and html.count("<details") == html.count("</details>")
    assert 'href="/taxas-de-referencia"' in html[html.index('id="referencia"'):html.index('id="aviso-minimo"')]


def test_simulador_js_le_e_grava_o_endereco_sem_dado_pessoal():
    js = open(os.path.join(RAIZ, "src", "simulador.js"), encoding="utf-8").read()
    assert "URLSearchParams" in js and "replaceState" in js and "copiou-link" in js
    assert ".innerHTML" not in js and "insertAdjacentHTML" not in js  # texto vindo do endereço nunca vira HTML
    assert "parcelas" in js and "cpf" not in js.lower()
