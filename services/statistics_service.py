from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import func
from models import db, Expense


def week_range(ref=None):
    """Semana de lunes a domingo."""
    ref = ref or date.today()
    inicio = ref - timedelta(days=ref.weekday())
    return inicio, inicio + timedelta(days=6)


def month_range(year, month):
    inicio = date(year, month, 1)
    siguiente = date(year + (month == 12), month % 12 + 1, 1)
    return inicio, siguiente - timedelta(days=1)


def get_period_total(user_id, start, end):
    total = (
        db.session.query(func.coalesce(func.sum(Expense.amount), 0))
        .filter(Expense.user_id == user_id,
                Expense.date >= start, Expense.date <= end)
        .scalar()
    )
    return Decimal(str(total))


def count_expenses(user_id, start, end):
    return (
        Expense.query.filter(Expense.user_id == user_id,
                             Expense.date >= start, Expense.date <= end)
        .count()
    )


def expenses_by_category(user_id, start, end):
    rows = (
        db.session.query(Expense.category, func.sum(Expense.amount))
        .filter(Expense.user_id == user_id,
                Expense.date >= start, Expense.date <= end)
        .group_by(Expense.category)
        .order_by(func.sum(Expense.amount).desc())
        .all()
    )
    return [{"category": c, "total": float(t)} for c, t in rows]


def compare_totals(total_a, total_b):
    a, b = Decimal(str(total_a)), Decimal(str(total_b))
    diff = b - a
    pct = (diff / a * 100) if a != 0 else None
    return {
        "period_a": float(a),
        "period_b": float(b),
        "difference": float(diff),
        "percentage": round(float(pct), 2) if pct is not None else None,
    }


def compare_periods(user_id, a_start, a_end, b_start, b_end):
    resultado = compare_totals(
        get_period_total(user_id, a_start, a_end),
        get_period_total(user_id, b_start, b_end),
    )
    cat_a = {x["category"]: x["total"]
             for x in expenses_by_category(user_id, a_start, a_end)}
    cat_b = {x["category"]: x["total"]
             for x in expenses_by_category(user_id, b_start, b_end)}
    dif = [
        {"category": c, "difference": round(cat_b.get(c, 0) - cat_a.get(c, 0), 2)}
        for c in set(cat_a) | set(cat_b)
    ]
    dif.sort(key=lambda x: abs(x["difference"]), reverse=True)
    resultado["by_category"] = dif
    return resultado


def chart_by_category(user_id, start, end):
    datos = expenses_by_category(user_id, start, end)
    return {"labels": [d["category"] for d in datos],
            "values": [d["total"] for d in datos]}


def summary(user_id, ref=None):
    ref = ref or date.today()
    ws, we = week_range(ref)
    ms, me = month_range(ref.year, ref.month)
    return {
        "day": float(get_period_total(user_id, ref, ref)),
        "week": float(get_period_total(user_id, ws, we)),
        "month": float(get_period_total(user_id, ms, me)),
        "movements_month": count_expenses(user_id, ms, me),
    }

MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
         "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


def shift_month(year, month, delta):
    """Mes (año, mes) desplazado `delta` meses; delta puede ser negativo."""
    idx = year * 12 + (month - 1) + delta
    return idx // 12, idx % 12 + 1


def get_category_total(user_id, category, start, end):
    total = (
        db.session.query(func.coalesce(func.sum(Expense.amount), 0))
        .filter(Expense.user_id == user_id, Expense.category == category,
                Expense.date >= start, Expense.date <= end)
        .scalar()
    )
    return Decimal(str(total))


def monthly_totals(user_id, months=6, ref=None):
    """Gasto total de los últimos `months` meses (el actual al final)."""
    ref = ref or date.today()
    labels, values = [], []
    for i in range(months - 1, -1, -1):
        y, m = shift_month(ref.year, ref.month, -i)
        ini, fin = month_range(y, m)
        labels.append(f"{MESES[m - 1]} {y}")
        values.append(float(get_period_total(user_id, ini, fin)))
    return {"labels": labels, "values": values}
