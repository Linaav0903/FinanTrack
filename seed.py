"""Carga una cuenta de demostración con datos de ejemplo.

Uso:  py seed.py
Entra con:  demo@finantrack.com  /  demo1234
Se puede ejecutar varias veces: reemplaza los datos de la cuenta demo.
"""
from datetime import date, timedelta

from app import app
from models import db, User, Expense, SavingsGoal, SavingsDeposit, Budget
from services import auth_service, savings_service, budget_service, statistics_service as st
from services.expense_service import create_expense

CORREO, CLAVE = "demo@finantrack.com", "demo1234"
hoy = date.today()

with app.app_context():
    user = User.query.filter_by(email=CORREO).first()
    if user is None:
        user = auth_service.register_user("Ana Demo", CORREO, CLAVE)
    uid = user.id
    for modelo in (Expense, SavingsDeposit, SavingsGoal, Budget):
        modelo.query.filter_by(user_id=uid).delete()
    db.session.commit()

    # Gastos del mes actual
    actuales = [(120, "Comida", 0), (45, "Transporte", 0), (85.5, "Comida", 1),
                (300, "Escuela", 2), (150, "Entretenimiento", 3), (90, "Comida", 5)]
    for monto, cat, dias in actuales:
        create_expense(uid, monto, cat, hoy - timedelta(days=dias), "Ejemplo")

    # Gastos de los 5 meses anteriores (para la gráfica y la comparación)
    base = [(320, "Comida"), (210, "Transporte"), (280, "Escuela"), (130, "Entretenimiento")]
    for i in range(1, 6):
        y, m = st.shift_month(hoy.year, hoy.month, -i)
        for k, (monto, cat) in enumerate(base):
            create_expense(uid, monto + i * 15 * (k % 2), cat, date(y, m, 4 + k * 6), "Ejemplo")

    # Presupuestos
    budget_service.set_budget(uid, "", 900)
    budget_service.set_budget(uid, "Comida", 250)
    budget_service.set_budget(uid, "Entretenimiento", 120)

    # Metas de ahorro con abonos
    laptop = savings_service.create_goal(uid, "Laptop nueva", 12000, hoy + timedelta(days=150))
    viaje = savings_service.create_goal(uid, "Viaje a la playa", 3000)
    fondo = savings_service.create_goal(uid, "Fondo de emergencia", 5000)
    for i, monto in enumerate([800, 1200, 900, 1000, 600]):
        y, m = st.shift_month(hoy.year, hoy.month, -i)
        savings_service.add_deposit(uid, laptop.id, monto, date(y, m, 10))
    savings_service.add_deposit(uid, viaje.id, 2000, hoy - timedelta(days=40))
    savings_service.add_deposit(uid, viaje.id, 1000, hoy - timedelta(days=3))
    savings_service.add_deposit(uid, fondo.id, 500, hoy - timedelta(days=9))

    print(f"Listo. Entra con {CORREO} / {CLAVE}")
