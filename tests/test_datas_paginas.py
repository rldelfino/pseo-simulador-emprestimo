"""A data de atualização de cada página só muda quando o conteúdo da página muda (e não a cada geração do site)."""
import datetime
import json
import os
import re

import gerador_emprestimo as g
import feed_atom

D1 = datetime.date(2026, 11, 17)
D2 = datetime.date(2026, 11, 24)


def ler(pasta, nome):
    with open(os.path.join(str(pasta), nome), encoding="utf-8") as f:
        return f.read()


def lastmods(pasta):
    return dict(re.findall(r"<loc>https://[^/]+(/[^<]*)</loc><lastmod>([^<]+)</lastmod>", ler(pasta, "sitemap.xml")))


def gerar(tmp_path, nome, dia, manifesto):
    pasta = tmp_path / nome
    g.gerar_site(str(pasta), hoje=dia, manifesto=str(manifesto))
    return pasta


def test_sem_mudar_nada_a_pagina_e_o_sitemap_mantem_a_data(tmp_path):
    m = tmp_path / "datas.json"
    a = gerar(tmp_path, "a", D1, m)
    b = gerar(tmp_path, "b", D2, m)  # uma semana depois, conteúdo igual
    assert set(lastmods(b).values()) == {"2026-11-17"}
    for nome in ("index.html", "como-funciona.html", "taxas-de-referencia.html", "termos.html", "sitemap.xml", "llms.txt"):
        assert ler(a, nome) == ler(b, nome), nome
    assert "Atualizado em 17/11/2026" in ler(b, "como-funciona.html") and "24/11/2026" not in ler(b, "como-funciona.html")
    assert '"dateModified": "2026-11-17"' in ler(b, "como-funciona.html")


def test_so_a_pagina_que_mudou_recebe_a_data_nova(tmp_path, monkeypatch):
    m = tmp_path / "datas.json"
    gerar(tmp_path, "a", D1, m)
    monkeypatch.setattr(g, "HOME_DESC", g.HOME_DESC + " Texto novo.")
    b = gerar(tmp_path, "b", D2, m)
    datas = lastmods(b)
    assert datas["/"] == "2026-11-24"
    assert {v for k, v in datas.items() if k != "/"} == {"2026-11-17"}
    assert "Atualizado em 24/11/2026" in ler(b, "index.html")
    assert "Atualizado em 17/11/2026" in ler(b, "sobre.html")
    assert "2026-11-24" in ler(b, "llms.txt") or "24/11/2026" in ler(b, "llms.txt")  # llms.txt traz a data da página mais recente


def test_mudar_so_a_versao_do_css_ou_do_js_nao_muda_a_data(tmp_path, monkeypatch):
    m = tmp_path / "datas.json"
    gerar(tmp_path, "a", D1, m)
    monkeypatch.setattr(g, "versao_css", lambda: "abc123def0")
    monkeypatch.setattr(g, "versao_menu_js", lambda: "0123456789")
    b = gerar(tmp_path, "b", D2, m)
    assert set(lastmods(b).values()) == {"2026-11-17"}


def test_mudanca_nos_dados_do_bcb_atualiza_a_pagina_de_taxas(tmp_path, monkeypatch):
    import taxas_referencia as tr
    m = tmp_path / "datas.json"
    gerar(tmp_path, "a", D1, m)
    linhas = tr.ler()
    linhas[-1] = dict(linhas[-1], taxa_aa=linhas[-1]["taxa_aa"] + 1.0)
    monkeypatch.setattr(tr, "ler", lambda *a, **k: linhas)
    b = gerar(tmp_path, "b", D2, m)
    assert lastmods(b)["/taxas-de-referencia"] == "2026-11-24"
    assert lastmods(b)["/como-funciona"] == "2026-11-17"


def test_manifesto_e_estavel_e_sem_dado_pessoal(tmp_path):
    m = tmp_path / "datas.json"
    gerar(tmp_path, "a", D1, m)
    primeiro = m.read_text(encoding="utf-8")
    gerar(tmp_path, "b", D2, m)
    assert m.read_text(encoding="utf-8") == primeiro  # nada mudou: o arquivo nem é regravado
    dados = json.loads(primeiro)
    assert set(dados) == {"index"} | {pg["slug"] for pg in g.conteudo.PAGINAS}
    for v in dados.values():
        assert set(v) == {"hash", "data"} and re.fullmatch(r"[0-9a-f]{10}", v["hash"]) and v["data"] == "2026-11-17"


def test_manifesto_ausente_ou_quebrado_nao_derruba_a_geracao(tmp_path):
    m = tmp_path / "datas.json"
    m.write_text("{isto não é json", encoding="utf-8")
    pasta = gerar(tmp_path, "a", D1, m)
    assert set(lastmods(pasta).values()) == {"2026-11-17"}
    assert json.loads(m.read_text(encoding="utf-8"))  # foi reescrito certo


def test_feed_nao_avanca_so_porque_o_site_foi_gerado_de_novo():
    ultimo = max(e["data"] for e in feed_atom.entradas())
    assert "<updated>" + ultimo + "</updated>" in feed_atom.gerar(D2).split("<entry>")[0]
    assert feed_atom.gerar(D1) == feed_atom.gerar(D2)
