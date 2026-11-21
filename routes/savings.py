from flask import Blueprint, jsonify, request, session
from services import savings_service as ss

bp = Blueprint("savings", __name__, url_prefix="/api/savings")


def _uid():
    return session.get("user_id")


@bp.before_request
def _auth():
    if _uid() is None:
        return jsonify(error="No autenticado"), 401


@bp.errorhandler(ValueError)
def _err(e):
    return jsonify(error=str(e)), 400


@bp.get("/goals")
def listar():
    return jsonify(ss.list_goals(_uid()))


@bp.post("/goals")
def crear():
    d = request.get_json(force=True)
    g = ss.create_goal(_uid(), d.get("name"), d.get("target"), d.get("deadline") or None)
    return jsonify(ss.goal_to_dict(g)), 201


@bp.post("/goals/<int:gid>/deposits")
def abonar(gid):
    d = request.get_json(force=True)
    r = ss.add_deposit(_uid(), gid, d.get("amount"), d.get("date") or None)
    return (jsonify(r), 201) if r else (jsonify(error="No encontrada"), 404)


@bp.delete("/goals/<int:gid>")
def borrar(gid):
    ok = ss.delete_goal(_uid(), gid)
    return ("", 204) if ok else (jsonify(error="No encontrada"), 404)


@bp.get("/summary")
def resumen():
    return jsonify(ss.summary(_uid()))
