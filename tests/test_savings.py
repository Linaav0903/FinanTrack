import pytest
from datetime import date
from services import savings_service as ss


def test_crear_meta_y_progreso(app):
    g = ss.create_goal(1, "Laptop", 1000)
    r = ss.add_deposit(1, g.id, 250, date(2026, 11, 2))
    assert r["saved"] == 250.0 and r["percentage"] == 25.0
    assert r["remaining"] == 750.0 and r["completed"] is False


def test_meta_cumplida_no_pasa_de_100(app):
    g = ss.create_goal(1, "Viaje", 500)
    ss.add_deposit(1, g.id, 300)
    r = ss.add_deposit(1, g.id, 300)
    assert r["completed"] is True and r["percentage"] == 100.0 and r["remaining"] == 0.0


@pytest.mark.parametrize("nombre,monto", [("", 100), ("Meta", 0), ("Meta", -5), ("Meta", "abc")])
def test_meta_invalida(app, nombre, monto):
    with pytest.raises(ValueError):
        ss.create_goal(1, nombre, monto)


def test_abono_invalido(app):
    g = ss.create_goal(1, "Meta", 100)
    with pytest.raises(ValueError):
        ss.add_deposit(1, g.id, -10)


def test_aislamiento_entre_usuarios(app):
    g = ss.create_goal(1, "Meta", 100)
    assert ss.add_deposit(2, g.id, 10) is None
    assert ss.delete_goal(2, g.id) is False
    assert ss.list_goals(2) == []


def test_eliminar_meta_borra_abonos(app):
    g = ss.create_goal(1, "Meta", 100)
    ss.add_deposit(1, g.id, 40)
    assert ss.delete_goal(1, g.id) is True
    assert float(ss.total_saved(1)) == 0.0


def test_resumen_y_ahorro_mensual(app):
    g = ss.create_goal(1, "Meta", 1000)
    ss.add_deposit(1, g.id, 100, date(2026, 11, 2))
    ss.add_deposit(1, g.id, 50, date(2026, 10, 15))
    r = ss.summary(1, ref=date(2026, 11, 19))
    assert r["total_saved"] == 150.0 and r["goals_count"] == 1 and r["completed_count"] == 0
    assert r["monthly"]["labels"] == ["Jun 2026", "Jul 2026", "Ago 2026", "Sep 2026", "Oct 2026", "Nov 2026"]
    assert r["monthly"]["values"] == [0.0, 0.0, 0.0, 0.0, 50.0, 100.0]
