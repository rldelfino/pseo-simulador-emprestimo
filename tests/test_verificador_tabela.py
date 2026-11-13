"""O verificador semanal acusa quando a API do parceiro deixa de bater com a nossa conta (API simulada, sem rede)."""
import copy

import calculo
import verificar_tabela_pix as v


def resposta_do_parceiro(corpo, mudar=None):
    n = corpo["parcels"]
    r = calculo.simular("valor", corpo["desiredValue"], 0, n)
    dados = {"parcelAmount": round(r["parcela"], 2), "grossAmount": round(r["total"], 2), "iofAmount": round(r["iof"], 2),
             "interestMonthly": r["jurosMes"], "cetAnnual": r["cetAno"], "tableName": "TABELA 10"}
    if mudar:
        dados.update(mudar(n, dados))
    return dados


def preparar(monkeypatch, limites=None, mudar=None):
    monkeypatch.setattr(v, "post", lambda corpo: resposta_do_parceiro(corpo, mudar))
    monkeypatch.setattr(v, "get", lambda url: limites or {"maxNetAmount": 5000, "maxParcels": 12})
    monkeypatch.setattr("sys.argv", ["verificar_tabela_pix.py"])


def test_tudo_igual_sai_com_zero(monkeypatch, capsys):
    preparar(monkeypatch)
    assert v.main() == 0
    assert "OK" in capsys.readouterr().out


def test_parcela_diferente_sai_com_um(monkeypatch, capsys):
    preparar(monkeypatch, mudar=lambda n, d: {"parcelAmount": d["parcelAmount"] + 1} if n == 7 else {})
    assert v.main() == 1
    assert "7x" in capsys.readouterr().out


def test_teto_ou_prazo_novo_sai_com_um(monkeypatch):
    preparar(monkeypatch, limites={"maxNetAmount": 7000, "maxParcels": 12})
    assert v.main() == 1
    preparar(monkeypatch, limites={"maxNetAmount": 5000, "maxParcels": 18})
    assert v.main() == 1


def test_tabela_renomeada_sai_com_um(monkeypatch):
    preparar(monkeypatch, mudar=lambda n, d: {"tableName": "TABELA 11"})
    assert v.main() == 1
