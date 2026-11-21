from datetime import date as date_type
from decimal import Decimal, InvalidOperation
from models import db, Expense


def _monto(valor):
    try:
        m = Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("El importe no es válido.")
    if not m.is_finite() or m <= 0:
        raise ValueError("El importe debe ser mayor que cero.")
    return m


def _norm(valor):
    c = (valor or "").strip()
    return c[:1].upper() + c[1:]


def _categoria(valor):
    c = _norm(valor)
    if not c:
        raise ValueError("La categoría es obligatoria.")
    if len(c) > 50:
        raise ValueError("La categoría es demasiado larga (máximo 50).")
    return c


def _fecha(valor):
    if isinstance(valor, str):
        try:
            valor = date_type.fromisoformat(valor)
        except ValueError:
            raise ValueError("La fecha no es válida.")
    if not isinstance(valor, date_type):
        raise ValueError("La fecha no es válida.")
    return valor


def create_expense(user_id, amount, category, date, description=""):
    gasto = Expense(
        user_id=user_id,
        amount=_monto(amount),
        category=_categoria(category),
        date=_fecha(date),
        description=(description or "").strip(),
    )
    db.session.add(gasto)
    db.session.commit()
    return gasto


def get_expense_by_id(user_id, expense_id):
    return Expense.query.filter_by(id=expense_id, user_id=user_id).first()


def filter_expenses(user_id, start_date=None, end_date=None, category=None):
    q = Expense.query.filter_by(user_id=user_id)
    if start_date:
        q = q.filter(Expense.date >= _fecha(start_date))
    if end_date:
        q = q.filter(Expense.date <= _fecha(end_date))
    if category:
        q = q.filter(Expense.category == _norm(category))
    return q.order_by(Expense.date.desc(), Expense.id.desc()).all()


def get_expenses(user_id):
    return filter_expenses(user_id)


def update_expense(user_id, expense_id, changes):
    gasto = get_expense_by_id(user_id, expense_id)
    if gasto is None:
        return None
    if "amount" in changes:
        gasto.amount = _monto(changes["amount"])
    if "category" in changes:
        gasto.category = _categoria(changes["category"])
    if "date" in changes:
        gasto.date = _fecha(changes["date"])
    if "description" in changes:
        gasto.description = (changes["description"] or "").strip()
    db.session.commit()
    return gasto


def delete_expense(user_id, expense_id):
    gasto = get_expense_by_id(user_id, expense_id)
    if gasto is None:
        return False
    db.session.delete(gasto)
    db.session.commit()
    return True