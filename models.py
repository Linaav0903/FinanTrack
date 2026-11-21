from datetime import date, datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Expense(db.Model):
    __tablename__ = "expenses"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(200), default="")


class SavingsGoal(db.Model):
    __tablename__ = "savings_goals"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    name = db.Column(db.String(80), nullable=False)
    target = db.Column(db.Numeric(12, 2), nullable=False)
    deadline = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.Date, default=date.today)


class SavingsDeposit(db.Model):
    __tablename__ = "savings_deposits"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    goal_id = db.Column(db.Integer, nullable=False, index=True)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    date = db.Column(db.Date, nullable=False)


class Budget(db.Model):
    """Límite mensual. category == "" significa límite del total de gastos."""
    __tablename__ = "budgets"
    __table_args__ = (db.UniqueConstraint("user_id", "category"),)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, default="")
    amount = db.Column(db.Numeric(12, 2), nullable=False)
