from datetime import date
from services import expense_service as es, statistics_service as st


def test_week_range_lunes_a_domingo():
    ini, fin = st.week_range(date(2026, 11, 18))  # miércoles
    assert ini == date(2026, 11, 16)
    assert fin == date(2026, 11, 22)


def test_month_range_noviembre_y_diciembre():
    assert st.month_range(2026, 11) == (date(2026, 11, 1), date(2026, 11, 30))
    assert st.month_range(2026, 12) == (date(2026, 12, 1), date(2026, 12, 31))


def test_periodo_vacio_da_cero(app):
    total = st.get_period_total(1, date(2026, 11, 1), date(2026, 11, 30))
    assert float(total) == 0


def test_total_no_mezcla_usuarios(app):
    es.create_expense(1, 100, "Comida", date(2026, 11, 5))
    es.create_expense(2, 999, "Comida", date(2026, 11, 5))
    total = st.get_period_total(1, date(2026, 11, 1), date(2026, 11, 30))
    assert float(total) == 100


def test_categorias_ordenadas_y_chart(app):
    es.create_expense(1, 50, "Comida", date(2026, 11, 1))
    es.create_expense(1, 70, "Comida", date(2026, 11, 2))
    es.create_expense(1, 30, "Escuela", date(2026, 11, 3))
    ini, fin = date(2026, 11, 1), date(2026, 11, 30)

    cats = st.expenses_by_category(1, ini, fin)
    assert cats == [{"category": "Comida", "total": 120.0},
                    {"category": "Escuela", "total": 30.0}]

    chart = st.chart_by_category(1, ini, fin)
    assert chart == {"labels": ["Comida", "Escuela"], "values": [120.0, 30.0]}


def test_summary(app):
    es.create_expense(1, 10, "Comida", date(2026, 11, 18))   # hoy
    es.create_expense(1, 20, "Comida", date(2026, 11, 16))   # misma semana
    es.create_expense(1, 30, "Escuela", date(2026, 11, 2))   # mismo mes
    es.create_expense(1, 99, "Escuela", date(2026, 10, 30))  # otro mes
    r = st.summary(1, ref=date(2026, 11, 18))
    assert r == {"day": 10.0, "week": 30.0, "month": 60.0,
                 "movements_month": 3}


def test_compare_totals():
    r = st.compare_totals(100, 150)
    assert r["difference"] == 50.0
    assert r["percentage"] == 50.0


def test_compare_contra_periodo_vacio():
    r = st.compare_totals(0, 150)
    assert r["percentage"] is None
    assert r["difference"] == 150.0


def test_compare_periods_con_categorias(app):
    es.create_expense(1, 100, "Comida", date(2026, 11, 3))   # periodo A
    es.create_expense(1, 150, "Comida", date(2026, 11, 10))  # periodo B
    es.create_expense(1, 50, "Escuela", date(2026, 11, 11))  # periodo B

    r = st.compare_periods(1,
                           date(2026, 11, 1), date(2026, 11, 7),
                           date(2026, 11, 8), date(2026, 11, 14))
    assert r["period_a"] == 100.0
    assert r["period_b"] == 200.0
    assert r["difference"] == 100.0
    assert r["percentage"] == 100.0
    assert {"category": "Comida", "difference": 50.0} in r["by_category"]
    assert {"category": "Escuela", "difference": 50.0} in r["by_category"]

def test_shift_month_cruza_anios():
    assert st.shift_month(2026, 11, 0) == (2026, 11)
    assert st.shift_month(2026, 1, -1) == (2025, 12)
    assert st.shift_month(2026, 11, -11) == (2025, 12)
    assert st.shift_month(2026, 12, 1) == (2027, 1)


def test_monthly_totals_seis_meses(app):
    es.create_expense(1, 100, "Comida", date(2026, 11, 2))
    es.create_expense(1, 40, "Comida", date(2026, 11, 9))
    es.create_expense(1, 70, "Escuela", date(2026, 10, 15))
    es.create_expense(1, 5, "Comida", date(2026, 5, 31))      # fuera de la ventana
    r = st.monthly_totals(1, 6, ref=date(2026, 11, 19))
    assert r["labels"] == ["Jun 2026", "Jul 2026", "Ago 2026", "Sep 2026", "Oct 2026", "Nov 2026"]
    assert r["values"] == [0.0, 0.0, 0.0, 0.0, 70.0, 140.0]


def test_total_por_categoria(app):
    es.create_expense(1, 10, "Comida", date(2026, 11, 2))
    es.create_expense(1, 20, "Escuela", date(2026, 11, 3))
    es.create_expense(2, 99, "Comida", date(2026, 11, 3))
    total = st.get_category_total(1, "Comida", date(2026, 11, 1), date(2026, 11, 30))
    assert float(total) == 10.0
