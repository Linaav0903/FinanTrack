from datetime import date
from decimal import Decimal
from models import db, Budget
from services.expense_service import _monto, _norm
from services import statistics_service as st

AVISO = 80  # % del límite a partir del cual se avisa


def set_budget(user_id, category, amount):
    """Crea o actualiza el límite mensual. category vacía = total del mes."""
    cat = _norm(category)
    if len(cat) > 50:
        raise ValueError("La categoría es demasiado larga (máximo 50).")
    monto = _monto(amount)
    b = Budget.query.filter_by(user_id=user_id, category=cat).first()
    if b is None:
        b = Budget(user_id=user_id, category=cat, amount=monto)
        db.session.add(b)
    else:
        b.amount = monto
    db.session.commit()
    return b


def delete_budget(user_id, budget_id):
    b = Budget.query.filter_by(id=budget_id, user_id=user_id).first()
    if b is None:
        return False
    db.session.delete(b)
    db.session.commit()
    return True


def budgets_status(user_id, ref=None):
    ref = ref or date.today()
    ini, fin = st.month_range(ref.year, ref.month)
    out = []
    for b in Budget.query.filter_by(user_id=user_id).order_by(Budget.category).all():
        limite = Decimal(str(b.amount))
        if b.category == "":
            gastado = st.get_period_total(user_id, ini, fin)
        else:
            gastado = st.get_category_total(user_id, b.category, ini, fin)
        pct = float(gastado / limite * 100) if limite else 0.0
        estado = "over" if pct > 100 else "warning" if pct >= AVISO else "ok"
        out.append({
            "id": b.id,
            "category": b.category,
            "label": b.category or "Total del mes",
            "limit": float(limite),
            "spent": float(gastado),
            "remaining": float(limite - gastado),
            "percentage": round(pct, 1),
            "state": estado,
        })
    out.sort(key=lambda x: (x["category"] != "", x["category"]))
    return out
