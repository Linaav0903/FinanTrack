from flask import Blueprint, jsonify, request, session
from services import budget_service as bs

bp = Blueprint("budgets", __name__, url_prefix="/api/budgets")


def _uid():
    return session.get("user_id")


@bp.before_request
def _auth():
    if _uid() is None:
        return jsonify(error="No autenticado"), 401


@bp.errorhandler(ValueError)
def _err(e):
    return jsonify(error=str(e)), 400


@bp.get("")
def listar():
    return jsonify(bs.budgets_status(_uid()))


@bp.post("")
def guardar():
    d = request.get_json(force=True)
    bs.set_budget(_uid(), d.get("category", ""), d.get("amount"))
    return jsonify(bs.budgets_status(_uid())), 201


@bp.delete("/<int:bid>")
def borrar(bid):
    ok = bs.delete_budget(_uid(), bid)
    return ("", 204) if ok else (jsonify(error="No encontrado"), 404)
