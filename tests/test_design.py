"""Design: o mesmo template dos simuladores irmãos (CSS à mão, tema escuro, destaque roxo), fontes próprias, sem estilo inline, nome correto do produto."""
import datetime
import hashlib
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
    css = open(os.path.join(RAIZ, "src", "estilo.css"), encoding="utf-8").read()
    for nome in FONTES:
        assert "/fonts/" + nome in css
    assert "Playfair Display" in css and "'Inter'" in css
    assert "googleapis" not in css and "gstatic" not in css


def test_nao_ha_mais_tailwind_nem_etapa_de_build_do_css():
    for nome in ("package.json", "tailwind.config.js", os.path.join("src", "input.css")):
        assert not os.path.exists(os.path.join(RAIZ, nome)), nome
    for wf in ("ci.yml", "atualiza_taxas.yml"):
        texto = open(os.path.join(RAIZ, ".github", "workflows", wf), encoding="utf-8").read()
        assert "npm" not in texto, wf


def test_nenhuma_pagina_chama_google_fonts_nem_tem_estilo_inline(site):
    for nome in paginas():
        html = ler(site, nome)
        assert "googleapis" not in html and "gstatic" not in html, nome
        assert " style=" not in html and "<style" not in html, nome
    cab = ler(site, "_headers")
    assert "googleapis" not in cab and "gstatic" not in cab
    assert "font-src 'self'" in cab and "/fonts/*" in cab and "immutable" in cab


def test_fontes_pre_carregadas_e_logo_svg_no_cabecalho(site):
    for nome in paginas():
        html = ler(site, nome)
        for f in FONTES:
            assert '<link rel="preload" href="/fonts/' + f + '"' in html, (nome, f)
        cab = html[html.index("<header"):html.index("</header>")]
        assert "<svg" in cab and 'href="/#simulador"' in html and "Empréstimo com crédito do cartão" in cab, nome
        assert "logo-full.png" not in html and "logo-header" not in html
    for velho in ("logo-full.png", "logo-header.webp", "logo-mark.png"):
        assert not os.path.exists(os.path.join(RAIZ, "paginas_seo", velho)), velho


def test_rodape_em_colunas_linka_todas_as_paginas_e_os_irmaos(site):
    for nome in paginas():
        html = ler(site, nome)
        rodape = html[html.index("<footer"):]
        for pg in conteudo.PAGINAS:
            assert 'href="/' + pg["slug"] + '"' in rodape, (nome, pg["slug"])
        assert 'href="/feed.xml"' in rodape
        # os outros simuladores da Datalab Global: links diretos (sem redirecionamento) com texto que descreve o destino
        assert 'href="https://simulador.datalabglobal.com/">Financiamento imobiliário</a>' in rodape, nome
        assert 'href="https://veiculos.datalabglobal.com/">Financiamento de veículos</a>' in rodape, nome
        assert 'href="https://homeequity.datalabglobal.com/">' in rodape, nome
        assert 'href="https://autoequity.datalabglobal.com/">' in rodape, nome
        assert 'href="https://condominio.datalabglobal.com/">' in rodape, nome
        assert 'href="' + g.HUB + '/">Datalab Global</a>' in rodape, nome


def test_menu_do_celular_nativo_sem_javascript(site):
    html = ler(site, "index.html")
    assert '<details class="menu">' in html and "<summary>Menu</summary>" in html
    menu = html[html.index('aria-label="Menu"'):html.index("</header>")]
    for s in g.ENTENDA:
        assert 'href="/' + s + '"' in menu


def test_home_tem_o_template_novo(site):
    html = ler(site, "index.html")
    for i in ("btn-modo-valor", "btn-modo-limite", "campo-valor", "range-valor", "range-parcelas", "r-parcela", "r-total", "r-receber", "r-iof", "r-cet", "r-juros",
              "k-real", "donut", "barras", "txt-barras", "btn-cta", "btn-parceiro", "dlg-confirma", "aviso-celular", "aviso-minimo", "leg-valor", "leg-custo",
              "campo-prop", "msg-prop", "det-prop", "nota-limite", "r-resumo"):
        assert 'id="' + i + '"' in html, i
    assert html.count("<h1") == 1
    for classe in ('class="grid" id="simulador"', 'class="panel resp"', 'class="kpis"', 'class="band"', 'class="rosca"', 'class="callout"', 'class="cta"'):
        assert classe in html, classe
    assert "glass-panel" not in html and "bg-gradient" not in html  # nada do Tailwind antigo
    assert html.count("<div") == html.count("</div>") and html.count("<details") == html.count("</details>")


def test_guias_com_cabecalho_em_selo_botao_de_voltar_e_painel(site):
    for pg in conteudo.PAGINAS:
        html = ler(site, pg["slug"] + ".html")
        assert 'class="guia"' in html and 'class="prose"' in html and "data-volta" in html, pg["slug"]
        assert html.count("<h1") == 1


def test_paleta_e_roxa_e_nao_usa_o_verde_do_imobiliario_nem_o_azul_dos_veiculos():
    css = open(os.path.join(RAIZ, "src", "estilo.css"), encoding="utf-8").read()
    js = open(os.path.join(RAIZ, "src", "simulador.js"), encoding="utf-8").read()
    for fonte in (css, js):
        assert "#10b981" not in fonte and "#34d399" not in fonte and "16, 185, 129" not in fonte
        assert "#4aa3b5" not in fonte and "74,163,181" not in fonte  # o azul-petróleo é do Home Equity
    assert "--ac:#a78bfa" in css and "#8b5cf6" in js
    for texto in (layout.HOME_MAIN, layout.LAYOUT, layout.LOGO):
        assert "emerald" not in texto and "teal" not in texto and "green" not in texto


def test_simulador_js_sem_innerhtml_e_com_rosca_e_barras():
    js = open(os.path.join(RAIZ, "src", "simulador.js"), encoding="utf-8").read()
    assert ".innerHTML" not in js and "insertAdjacentHTML" not in js  # só textContent e atributos SVG
    assert "desenharRosca" in js and "desenharBarras" in js and "marcarSlider" in js


def test_css_tem_versao_no_endereco_e_bate_com_o_arquivo(site):
    """styles.css tem cache imutável de 1 ano: sem a versão no endereço, quem já visitou ficaria com o CSS velho."""
    esperado = hashlib.sha256(open(os.path.join(RAIZ, "src", "estilo.css"), "rb").read()).hexdigest()[:10]
    assert g.versao_css() == esperado
    for nome in paginas() + ["404.html"]:
        html = ler(site, nome)
        assert 'href="/styles.css?v=' + esperado + '"' in html or nome == "404.html", nome
        assert 'href="/styles.css"' not in html or nome == "404.html", nome
    assert (site / "styles.css").read_bytes() == open(os.path.join(RAIZ, "src", "estilo.css"), "rb").read()


def test_slider_tem_uma_regra_de_preenchimento_por_valor():
    css = open(os.path.join(RAIZ, "src", "estilo.css"), encoding="utf-8").read()
    for n in range(0, 101):
        assert 'input[type=range][data-p="%d"]' % n in css, n


def test_scripts_tem_versao_no_endereco_e_bate_com_o_conteudo(site):
    """O Cloudflare guarda .js na borda por horas: sem ?v=, o HTML novo podia receber o JS antigo (aconteceu no deploy do redesign)."""
    html = ler(site, "index.html")
    assert 'src="/calculo.js?v=' + g.versao_calculo_js() + '"' in html
    assert 'src="/simulador.js?v=' + g.versao_simulador_js() + '"' in html
    assert 'src="/simulador.js"' not in html and 'src="/calculo.js"' not in html
    assert g.versao_simulador_js() != g.versao_calculo_js()
    # o conteúdo servido é o do src (o gerador copia o arquivo sem alterar)
    assert (site / "simulador.js").read_bytes() == open(os.path.join(RAIZ, "src", "simulador.js"), "rb").read()


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
    texto = conteudo.custo_home()
    assert texto.startswith("Os juros vão de 34,64% ao mês (2x) a 7,49% ao mês (12x).")
    assert "3.621,21% a 148,97%" in texto


def test_titulos_cabem_no_resultado_do_google():
    for pg in conteudo.PAGINAS:
        assert len(pg["title"]) <= 60, (pg["slug"], len(pg["title"]))
    assert len(g.HOME_TITLE) <= 60 and len(g.HOME_DESC) <= 160


def test_abas_com_painel_campo_de_texto_barra_fixa_e_aviso_da_proposta(site):
    html = ler(site, "index.html")
    assert html.count('aria-controls="painel-simulacao"') == 2 and 'id="painel-simulacao" role="tabpanel"' in html
    assert 'id="campo-valor" type="text" inputmode="decimal"' in html
    for i in ("barra-resumo", "btn-resumo", "resultado", "aviso-proposta", "txt-aviso-proposta", "link-parceiro"):
        assert 'id="' + i + '"' in html, i


def test_modo_limite_aceita_a_partir_do_minimo_e_avisa_quando_falta_limite():
    js = open(os.path.join(RAIZ, "src", "simulador.js"), encoding="utf-8").read()
    assert "var LIMITE_MIN = 300;" in js and "limiteNecessario" in js
    assert "aria-valuetext" in js and "ArrowRight" in js and "IntersectionObserver" in js
    assert "cta-parceiro-sem-preenchimento" in js  # não segue calado quando o parceiro não responde


def test_confirmacao_vem_antes_do_parceiro_e_avisa_do_pedido_real(site):
    html = ler(site, "index.html")
    dlg = html[html.index('<dialog id="dlg-confirma"'):html.index("</dialog>")]
    assert "6 passos, com CPF e documento original" in dlg and "limite do seu cartão" in dlg
    assert 'id="btn-parceiro"' in dlg and "Continuar para o parceiro" in dlg and "Voltar e ajustar" in dlg
    # o botão da simulação só abre a tela de confirmação; o link do parceiro só existe dentro dela
    assert 'id="btn-cta"' in html[:html.index("<dialog")] and "Ver minha proposta" in html
    assert "checkoutonline" not in html[:html.index("<dialog")]
    assert 'rel="noopener sponsored"' in dlg
    js = open(os.path.join(RAIZ, "src", "simulador.js"), encoding="utf-8").read()
    assert "showModal" in js and "abriu-confirmacao" in js and "irParaParceiro" in js


def test_resultado_compara_com_o_bcb_e_copia_o_link(site):
    html = ler(site, "index.html")
    for i in ("referencia", "ref-lista", "ref-veredito", "ref-nota", "btn-copiar", "msg-copiado", "detalhe-prazos", "corpo-prazos", "cap-prazos"):
        assert 'id="' + i + '"' in html, i
    assert 'href="/taxas-de-referencia"' in html[html.index('id="referencia"'):html.index('id="ref-nota"') + 400]


def test_simulador_js_le_e_grava_o_endereco_sem_dado_pessoal():
    js = open(os.path.join(RAIZ, "src", "simulador.js"), encoding="utf-8").read()
    assert "URLSearchParams" in js and "replaceState" in js and "copiou-link" in js
    assert ".innerHTML" not in js and "insertAdjacentHTML" not in js  # texto vindo do endereço nunca vira HTML
    assert "parcelas" in js and "cpf" not in js.lower()


def test_campo_proposta_propria_com_taxa_e_evento():
    js = open(os.path.join(RAIZ, "src", "simulador.js"), encoding="utf-8").read()
    assert "taxaImplicita" in js and "usou-proposta-propria" in js and "'prop'" in js


def test_nome_do_produto_correto_em_todo_o_site(site):
    """O produto NÃO é "Pix no cartão" nem "Pix com cartão": é um empréstimo pessoal em que o limite do cartão é a fonte do dinheiro (entregue por Pix)."""
    for nome in paginas() + ["404.html", "llms.txt", "feed.xml", "sitemap.xml", "dados/README.md"]:
        texto = ler(site, nome).replace(g.dados_abertos.EMPRESTIMO["huggingface"], "")  # o endereço do dataset no Hugging Face foi criado com o nome antigo (só o dono renomeia)
        assert "Pix com cartão" not in texto and "pix-no-cartao" not in texto and "Pix parcelado" not in texto.replace("“Pix parcelado”", ""), nome
        # "Pix no cartão" só aparece, entre aspas, na FAQ que corrige quem procura por esse nome
        sem_faq = texto.replace("“Pix no cartão”", "")
        assert "Pix no cartão" not in sem_faq, nome
    home = ler(site, "index.html")
    assert "<title>Empréstimo pessoal com crédito do cartão: parcela e IOF</title>" in home
    assert "<h1>Empréstimo pessoal com <em>crédito do cartão</em></h1>" in home
    assert "limite do cartão" in home and "Já vi isso chamado de" in home
    assert conteudo.NOME in ler(site, "llms.txt") and conteudo.NOME in ler(site, "feed.xml")


def test_redirecionamentos_301_do_slug_antigo_e_dos_dados_antigos(site):
    r = ler(site, "_redirects")
    assert "/pix-no-cartao-ou-outro-credito /emprestimo-com-cartao-ou-outro-credito 301" in r
    assert "/dados/pix-no-cartao-tabela-10.csv /dados/emprestimo-cartao-tabela-10.csv 301" in r
    assert not (site / "pix-no-cartao-ou-outro-credito.html").exists()
    assert (site / "emprestimo-com-cartao-ou-outro-credito.html").exists()
    # sitemap, canonical e links internos só usam o endereço novo
    assert "emprestimo-com-cartao-ou-outro-credito" in ler(site, "sitemap.xml")
    for nome in paginas():
        assert 'href="/pix-no-cartao' not in ler(site, nome), nome


def test_arquivo_de_verificacao_do_yandex_no_site():
    caminho = os.path.join(RAIZ, "paginas_seo", "yandex_90c15c3be650b0ed.html")
    esperado = ('<html>\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">\n</head>\n'
                '<body>Verification: 90c15c3be650b0ed</body>\n</html>')
    assert open(caminho, encoding="utf-8", newline="").read() == esperado


def test_links_internos_existem(site):
    """Todo href interno aponta para uma página (ou arquivo) que o gerador produz; âncoras da home existem."""
    existentes = {"/", "/feed.xml"}
    for nome in os.listdir(site):
        if nome.endswith(".html"):
            existentes.add("/" + nome[:-5] if nome != "index.html" else "/")
    for raiz, _d, arqs in os.walk(site):
        for a in arqs:
            existentes.add("/" + os.path.relpath(os.path.join(raiz, a), site).replace(os.sep, "/"))
    home = ler(site, "index.html")
    ids_home = set(re.findall(r'id="([^"]+)"', home))
    for nome in paginas():
        html = ler(site, nome)
        for href in re.findall(r'href="(/[^"#?]*)(#[^"]*)?"', html):
            caminho, ancora = href
            assert caminho in existentes or caminho.rstrip("/") in existentes, (nome, caminho)
            if ancora and caminho in ("/", ""):
                assert ancora[1:] in ids_home, (nome, ancora)
