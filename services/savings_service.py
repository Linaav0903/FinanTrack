from datetime import date
from decimal import Decimal
from sqlalchemy import func
from models import db, SavingsGoal, SavingsDeposit
from services.expense_service import _monto, _fecha
from services import statistics_service as st

CENT = Decimal("0.01")


def _suma(query):
    return Decimal(str(query.scalar())).quantize(CENT)


def _saved(goal_id):
    return _suma(db.session.query(func.coalesce(func.sum(SavingsDeposit.amount), 0))
                 .filter(SavingsDeposit.goal_id == goal_id))


def goal_to_dict(goal):
    saved = _saved(goal.id)
    target = Decimal(str(goal.target))
    pct = float(saved / target * 100) if target else 0.0
    return {
        "id": goal.id,
        "name": goal.name,
        "target": float(target),
        "saved": float(saved),
        "remaining": float(max(target - saved, Decimal("0"))),
        "percentage": round(min(pct, 100.0), 1),
        "deadline": goal.deadline.isoformat() if goal.deadline else None,
        "completed": saved >= target,
    }


def create_goal(user_id, name, target, deadline=None):
    nombre = (name or "").strip()
    if not nombre:
        raise ValueError("El nombre de la meta es obligatorio.")
    if len(nombre) > 80:
        raise ValueError("El nombre de la meta es demasiado largo (máximo 80).")
    goal = SavingsGoal(user_id=user_id, name=nombre, target=_monto(target),
                       deadline=_fecha(deadline) if deadline else None)
    db.session.add(goal)
    db.session.commit()
    return goal


def get_goal(user_id, goal_id):
    return SavingsGoal.query.filter_by(id=goal_id, user_id=user_id).first()


def list_goals(user_id):
    goals = SavingsGoal.query.filter_by(user_id=user_id).order_by(SavingsGoal.id).all()
    return [goal_to_dict(g) for g in goals]


def add_deposit(user_id, goal_id, amount, on_date=None):
    """Abona a una meta. Devuelve None si la meta no existe o no es del usuario."""
    goal = get_goal(user_id, goal_id)
    if goal is None:
        return None
    dep = SavingsDeposit(user_id=user_id, goal_id=goal.id, amount=_monto(amount),
                         date=_fecha(on_date) if on_date else date.today())
    db.session.add(dep)
    db.session.commit()
    return goal_to_dict(goal)


def delete_goal(user_id, goal_id):
    goal = get_goal(user_id, goal_id)
    if goal is None:
        return False
    SavingsDeposit.query.filter_by(goal_id=goal.id, user_id=user_id).delete()
    db.session.delete(goal)
    db.session.commit()
    return True


def total_saved(user_id):
    return _suma(db.session.query(func.coalesce(func.sum(SavingsDeposit.amount), 0))
                 .filter(SavingsDeposit.user_id == user_id))


def savings_monthly(user_id, months=6, ref=None):
    ref = ref or date.today()
    labels, values = [], []
    for i in range(months - 1, -1, -1):
        y, m = st.shift_month(ref.year, ref.month, -i)
        ini, fin = st.month_range(y, m)
        total = _suma(db.session.query(func.coalesce(func.sum(SavingsDeposit.amount), 0))
                      .filter(SavingsDeposit.user_id == user_id,
                              SavingsDeposit.date >= ini, SavingsDeposit.date <= fin))
        labels.append(f"{st.MESES[m - 1]} {y}")
        values.append(float(total))
    return {"labels": labels, "values": values}


def summary(user_id, ref=None):
    goals = list_goals(user_id)
    return {
        "total_saved": float(total_saved(user_id)),
        "goals_count": len(goals),
        "completed_count": sum(1 for g in goals if g["completed"]),
        "monthly": savings_monthly(user_id, 6, ref),
    }
