import os
from functools import wraps

from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash)

from models import db
from routes.expenses import bp as expenses_bp
from routes.savings import bp as savings_bp
from routes.budgets import bp as budgets_bp
from services import auth_service


app = Flask(__name__)

# Configuración
app.secret_key = os.environ.get("SECRET_KEY", "finantrack_clave_desarrollo_2026")
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

DATABASE = os.path.join(app.root_path, "database.db")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + DATABASE.replace("\\", "/")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
app.register_blueprint(expenses_bp)
app.register_blueprint(savings_bp)
app.register_blueprint(budgets_bp)

with app.app_context():
    db.create_all()   # crea las tablas que falten (users, expenses, savings_*, budgets)


def login_required(vista):
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return vista(*args, **kwargs)
    return envoltura


def _iniciar_sesion(user):
    session.clear()
    session["user_id"] = user.id
    session["user_name"] = user.name


@app.context_processor
def datos_de_sesion():
    return {"logged_in": "user_id" in session,
            "user_name": session.get("user_name", "")}


# Página principal
@app.route("/")
def inicio():
    return render_template("index.html")


# Inicio de sesión
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form.get("correo", "")
        user = auth_service.authenticate(correo, request.form.get("password"))
        if user is None:
            flash("Correo o contraseña incorrectos.", "error")
            return render_template("login.html", correo=correo)
        _iniciar_sesion(user)
        return redirect(url_for("dashboard"))
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("login.html", correo="")


# Registro
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        f = request.form
        try:
            user = auth_service.register_user(
                f.get("nombre"), f.get("correo"),
                f.get("password"), f.get("confirmar"))
        except ValueError as e:
            flash(str(e), "error")
            return render_template("registro.html", nombre=f.get("nombre", ""),
                                   correo=f.get("correo", ""))
        _iniciar_sesion(user)
        return redirect(url_for("dashboard"))
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("registro.html", nombre="", correo="")


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("inicio"))


# Páginas de la aplicación (requieren sesión)
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/gastos")
@login_required
def gastos():
    return render_template("gastos.html")


@app.route("/ahorro")
@login_required
def ahorro():
    return render_template("ahorro.html")


@app.route("/presupuesto")
@login_required
def presupuesto():
    return render_template("presupuesto.html")


if __name__ == "__main__":
    app.run(debug=True)
