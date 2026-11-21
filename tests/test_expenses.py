import pytest
from datetime import date
from services import expense_service as es, statistics_service as st


def test_t01_crear(app):
    g = es.create_expense(1, 100, "Comida", date(2026, 11, 10))
    assert g.id and float(g.amount) == 100


def test_t02_negativo(app):
    with pytest.raises(ValueError):
        es.create_expense(1, -5, "Comida", date(2026, 11, 10))


def test_t03_editar(app):
    g = es.create_expense(1, 50, "Comida", date(2026, 11, 10))
    es.update_expense(1, g.id, {"category": "Escuela"})
    assert es.get_expense_by_id(1, g.id).category == "Escuela"


def test_t04_eliminar(app):
    g = es.create_expense(1, 50, "Comida", date(2026, 11, 10))
    assert es.delete_expense(1, g.id) is True
    assert es.get_expense_by_id(1, g.id) is None


def test_t05_t12_aislamiento(app):
    g = es.create_expense(1, 50, "Comida", date(2026, 11, 10))
    es.create_expense(2, 70, "Comida", date(2026, 11, 10))
    assert len(es.get_expenses(1)) == 1
    assert es.get_expense_by_id(2, g.id) is None
    assert es.delete_expense(2, g.id) is False


def test_t06_t07_filtros(app):
    es.create_expense(1, 10, "Comida", date(2026, 11, 1))
    es.create_expense(1, 20, "Transporte", date(2026, 11, 15))
    assert len(es.filter_expenses(1, category="Comida")) == 1
    assert len(es.filter_expenses(1, "2026-11-10", "2026-11-20")) == 1


def test_t08_t09_totales(app):
    es.create_expense(1, 10, "Comida", date(2026, 11, 1))
    es.create_expense(1, 20, "Comida", date(2026, 11, 2))
    es.create_expense(1, 30, "Escuela", date(2026, 11, 3))
    ini, fin = date(2026, 11, 1), date(2026, 11, 30)
    assert float(st.get_period_total(1, ini, fin)) == 60
    cats = st.expenses_by_category(1, ini, fin)
    assert cats[0] == {"category": "Escuela", "total": 30.0} or cats[0]["total"] == 30.0
    assert {"category": "Comida", "total": 30.0} in cats


def test_t10_t11_comparar():
    r = st.compare_totals(100, 150)
    assert r["difference"] == 50 and r["percentage"] == 50.0
    assert st.compare_totals(0, 150)["percentage"] is None

def test_categoria_se_normaliza(app):
    es.create_expense(1, 10, "comida", date(2026, 11, 1))
    assert es.get_expenses(1)[0].category == "Comida"
    assert len(es.filter_expenses(1, category="comida")) == 1
