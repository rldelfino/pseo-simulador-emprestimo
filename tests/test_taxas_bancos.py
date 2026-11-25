"""Taxas por banco: agregação do BCB (sem rede), nomes, ETL que não troca o arquivo com dado ruim."""
import taxas_bancos as tb
import etl_taxas_referencia as etl


def _janelas(cnpj, nome, taxa, n, inicio="2026-10-05"):
    import datetime
    d0 = datetime.date.fromisoformat(inicio)
    return [{"InicioPeriodo": (d0 + datetime.timedelta(days=i)).isoformat(), "FimPeriodo": (d0 + datetime.timedelta(days=i + 4)).isoformat(),
             "InstituicaoFinanceira": nome, "TaxaJurosAoMes": taxa, "TaxaJurosAoAno": taxa * 12, "cnpj8": cnpj} for i in range(n)]


def test_agregar_media_simples_e_minimo_de_janelas():
    regs = _janelas("1", "BANCO X S.A.", 2.0, 20) + _janelas("2", "BANCO Y S.A.", 4.0, 10) + _janelas("3", "BANCO Z S.A.", 3.0, 20)
    r = tb.agregar(regs)
    assert [x["cnpj8"] for x in r] == ["1", "3"]            # o de 10 janelas fica de fora; ordem alfabética
    assert r[0]["taxa_am"] == 2.0 and r[0]["janelas"] == 20


def test_agregar_descarta_taxa_fora_da_faixa():
    assert tb.agregar(_janelas("1", "X", 0.0, 20) + _janelas("2", "Y", 90.0, 20)) == []


def test_nomes_amigaveis():
    assert tb.nome_amigavel("60872504", "ITAU UNIBANCO HOLDING S.A.") == "Itaú Unibanco"
    assert tb.nome_amigavel("999", "BCO DO ESTADO S.A.") == "Banco do Estado"
    assert tb.nome_amigavel("998", "SAFRA S.A.") == "Safra"
    assert tb.nome_amigavel("997", "BANCO J.SAFRA S.A.") == "Banco J.Safra"


def test_csv_roundtrip(tmp_path):
    por_mod = {m["chave"]: tb.agregar(_janelas(str(i), "BANCO " + str(i), 2.0 + i, 20)) for i, m in enumerate(tb.MODALIDADES)}
    caminho = str(tmp_path / "t.csv")
    tb.salvar(por_mod, caminho)
    assert tb.ler(caminho) == por_mod


def test_etl_mantem_arquivo_quando_dado_pouco_confiavel(tmp_path, capsys):
    class R:
        def raise_for_status(self): pass
        def json(self): return {"value": _janelas("1", "BANCO X", 2.0, 20)}
    caminho = tmp_path / "t.csv"
    caminho.write_text("antigo", encoding="utf-8")
    assert etl.atualizar_bancos(str(caminho), get=lambda *a, **k: R()) is None
    assert caminho.read_text(encoding="utf-8") == "antigo"
    assert "AVISO taxas por banco" in capsys.readouterr().out
