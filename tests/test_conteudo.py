"""Fase 3: conteúdo com valor próprio, sem páginas quase iguais, sem ranking de bancos, com blocos de confiança."""
import datetime
import json
import os
import re

import pytest

import calculo
import conteudo
import gerador_emprestimo as g

BANCOS = ["Itaú", "Itau", "Bradesco", "Nubank", "Santander", "Banco do Brasil", "Caixa Econômica", "Banco Inter", "C6", "PicPay", "Mercado Pago", "BTG"]


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    pasta = tmp_path_factory.mktemp("site3")
    g.gerar_site(str(pasta), hoje=datetime.date(2026, 11, 14))
    return pasta


def ler(site, nome):
    return (site / nome).read_text(encoding="utf-8")


def principal(html):
    m = re.search(r"<main[^>]*>(.*)</main>", html, re.S)
    return m.group(1)


def texto(html):
    sem = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", sem.replace("&quot;", '"')).strip()


def arquivos_indexaveis():
    return ["index.html"] + [pg["slug"] + ".html" for pg in conteudo.PAGINAS if pg["slug"] not in g.SEM_INDICE]


def test_poucas_paginas_e_todas_geradas(site):
    assert len(g.PAGINAS_INDEXAVEIS) <= 30
    for nome in arquivos_indexaveis():
        assert (site / nome).exists(), nome
    assert g.PAGINAS_VALOR_INDEXAVEIS is False
    assert not [f for f in os.listdir(site) if re.match(r"pix-no-cartao-\d", f)]


def test_titulos_h1_e_canonicais_unicos(site):
    titulos, h1s, canon = [], [], []
    for nome in arquivos_indexaveis():
        html = ler(site, nome)
        titulos.append(re.search(r"<title>(.*?)</title>", html).group(1))
        h1s.append(re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.S))
        canon.append(re.search(r'rel="canonical" href="([^"]+)"', html).group(1))
        assert len(h1s[-1]) == 1, nome
        assert 'content="index,follow' in html and "noindex" not in html, nome
        desc = re.search(r'name="description" content="([^"]+)"', html).group(1)
        assert 70 <= len(desc) <= 200, (nome, len(desc))
    assert len(set(titulos)) == len(titulos)
    assert len({h[0] for h in h1s}) == len(h1s)
    assert len(set(canon)) == len(canon)


def test_cada_guia_tem_texto_proprio(site):
    for pg in conteudo.PAGINAS:
        if pg.get("guia", True):
            palavras = len(texto(principal(ler(site, pg["slug"] + ".html"))).split())
            assert palavras >= pg.get("min_palavras", 330), (pg["slug"], palavras)


def test_paginas_nao_sao_quase_iguais(site):
    def shingles(t, k=5):
        w = t.split()
        return {" ".join(w[i:i + k]) for i in range(len(w) - k + 1)}

    corpos = {n: shingles(texto(principal(ler(site, n)))) for n in arquivos_indexaveis()}
    nomes = list(corpos)
    for i in range(len(nomes)):
        for j in range(i + 1, len(nomes)):
            a, b = corpos[nomes[i]], corpos[nomes[j]]
            jac = len(a & b) / max(1, len(a | b))
            assert jac < 0.15, (nomes[i], nomes[j], round(jac, 3))


def test_links_internos_resolvem(site):
    for nome in arquivos_indexaveis():
        for href in re.findall(r'href="(/[^"]*)"', ler(site, nome)):
            if href.startswith("//"):
                continue
            caminho = href.split("#")[0]
            if caminho in ("", "/"):
                continue
            if "." in os.path.basename(caminho):
                continue  # arquivos estáticos (css, ico...)
            assert (site / (caminho.strip("/") + ".html")).exists(), (nome, href)


def test_sitemap_igual_as_paginas_geradas(site):
    urls = set(re.findall(r"<loc>([^<]+)</loc>", ler(site, "sitemap.xml")))
    esperado = {g.DOMINIO + "/"} | {g.DOMINIO + "/" + pg["slug"] for pg in conteudo.PAGINAS if pg["slug"] not in g.SEM_INDICE}
    assert urls == esperado
    for slug in g.SEM_INDICE:  # texto padrão: acessível, mas fora do índice
        assert 'content="noindex' in ler(site, slug + ".html"), slug
    llms = ler(site, "llms.txt")
    assert all(u in llms for u in esperado)


def test_nenhum_banco_citado_e_nada_de_ranking(site):
    for nome in arquivos_indexaveis():
        t = texto(ler(site, nome))
        for b in BANCOS:
            assert b not in t, (nome, b)
        assert "melhor banco" not in t.lower() and "ranking" not in t.lower().replace("não fazemos ranking", "")


def test_numeros_do_custo_vem_da_tabela(site):
    t = texto(ler(site, "custo-cet-iof.html"))
    r2, r12 = calculo.simular("valor", 1000, 0, 2), calculo.simular("valor", 1000, 0, 12)
    assert conteudo.brl(r12["total"]) == "R$ 1.583,90" and conteudo.brl(r2["total"]) == "R$ 1.553,90"
    for esperado in ("R$ 1.583,90", "R$ 1.553,90", "R$ 583,90", "R$ 553,90", "R$ 30,00", "R$ 131,99", "R$ 776,95", "148,97%", "3.621,21%", "34,64%", "7,49%"):
        assert esperado in t, esperado
    # uma linha por prazo na tabela
    assert len(re.findall(r"<tr>", ler(site, "custo-cet-iof.html"))) == 1 + len(calculo.PARCELAS)


def test_blocos_de_confianca(site):
    for nome in arquivos_indexaveis():
        html = ler(site, nome)
        assert "Atualizado em 14/11/2026" in html, nome
        assert g.CNPJ in html and g.RAZAO_SOCIAL in html, nome
        assert "comissão" not in texto(html).lower() and "remuneração" not in texto(html).lower(), nome  # 21/11/2026: dono mandou tirar a divulgação de comissão; fica só o link do parceiro
        assert "análise de crédito" in texto(html) or "Crédito sujeito a análise" in texto(html), nome
    assert "não há garantia" in texto(ler(site, "index.html")).lower() or "sem garantia de aprovação" in texto(ler(site, "index.html")).lower()
    # a Resolução CMN 3.954/2011 foi revogada (Res. BCB 277/2022): não pode aparecer como norma vigente em nenhuma página do site
    for nome in arquivos_indexaveis():
        corpo = texto(principal(ler(site, nome)))
        if nome != "atualizacoes.html":
            assert "3.954" not in corpo, nome
    assert "Lei nº 10.931/2004" in ler(site, "e-seguro-golpes.html")
    assert "Tabela 10" in ler(site, "metodologia.html") and "0,5479" in ler(site, "metodologia.html")


def test_json_ld_valido_e_faq_igual_ao_visivel(site):
    for nome in arquivos_indexaveis():
        for bloco in re.findall(r'<script type="application/ld\+json">(.*?)</script>', ler(site, nome), re.S):
            json.loads(bloco)
    home = ler(site, "index.html")
    blocos = [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', home, re.S)]
    faq = next(b for b in blocos if b.get("@type") == "FAQPage")
    assert len(faq["mainEntity"]) == len(conteudo.FAQ)
    visivel = texto(home)
    for q in faq["mainEntity"]:
        assert q["name"] in visivel


def test_umami_em_todas_as_paginas_e_simulador_so_na_home(site):
    for nome in arquivos_indexaveis():
        assert "cloud.umami.is/script.js" in ler(site, nome), nome
    assert "/simulador.js" in ler(site, "index.html")
    assert "/simulador.js" not in ler(site, "custo-cet-iof.html")


def test_sem_aviso_de_aprovacao_garantida(site):
    for nome in arquivos_indexaveis():
        t = texto(ler(site, nome)).lower()
        assert "aprovação garantida" not in t.replace("prometem aprovação garantida", "").replace("garantia de aprovação", "")
        assert "sem consulta" not in t and "sem análise" not in t
