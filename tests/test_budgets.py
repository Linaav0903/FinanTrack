import pytest
from datetime import date
from services import budget_service as bs, expense_service as es

HOY = date(2026, 11, 19)


def _datos():
    es.create_expense(1, 300, "Comida", date(2026, 11, 5))
    es.create_expense(1, 100, "Escuela", date(2026, 11, 6))
    es.create_expense(1, 60, "Salud", date(2026, 11, 7))
    es.create_expense(1, 500, "Comida", date(2026, 10, 30))   # otro mes: no cuenta


def test_estados_ok_aviso_y_excedido(app):
    _datos()
    bs.set_budget(1, "", 1000)          # total del mes: 460 de 1000
    bs.set_budget(1, "comida", 400)     # 300 de 400
    bs.set_budget(1, "Escuela", 110)    # 100 de 110
    bs.set_budget(1, "Salud", 50)       # 60 de 50
    r = {b["label"]: b for b in bs.budgets_status(1, ref=HOY)}
    assert r["Total del mes"]["spent"] == 460.0 and r["Total del mes"]["state"] == "ok"
    assert r["Comida"]["percentage"] == 75.0 and r["Comida"]["state"] == "ok"
    assert r["Escuela"]["percentage"] == 90.9 and r["Escuela"]["state"] == "warning"
    assert r["Salud"]["percentage"] == 120.0 and r["Salud"]["state"] == "over"
    assert r["Salud"]["remaining"] == -10.0


def test_total_del_mes_va_primero(app):
    bs.set_budget(1, "Comida", 100)
    bs.set_budget(1, "", 500)
    assert [b["label"] for b in bs.budgets_status(1, ref=HOY)] == ["Total del mes", "Comida"]


def test_guardar_de_nuevo_actualiza_sin_duplicar(app):
    bs.set_budget(1, "Comida", 100)
    bs.set_budget(1, "comida", 250)
    lista = bs.budgets_status(1, ref=HOY)
    assert len(lista) == 1 and lista[0]["limit"] == 250.0


@pytest.mark.parametrize("monto", [0, -1, "abc"])
def test_limite_invalido(app, monto):
    with pytest.raises(ValueError):
        bs.set_budget(1, "Comida", monto)


def test_aislamiento_y_borrado(app):
    b = bs.set_budget(1, "Comida", 100)
    assert bs.delete_budget(2, b.id) is False
    assert bs.budgets_status(2, ref=HOY) == []
    assert bs.delete_budget(1, b.id) is True
