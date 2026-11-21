from datetime import date
from flask import Blueprint, jsonify, request, session
from services import expense_service as es, statistics_service as st

bp = Blueprint("expenses", __name__, url_prefix="/api")


def _uid():
    return session.get("user_id")


def _ser(g):
    return {"id": g.id, "amount": float(g.amount), "category": g.category,
            "date": g.date.isoformat(), "description": g.description}


@bp.before_request
def _auth():
    if _uid() is None:
        return jsonify(error="No autenticado"), 401


@bp.errorhandler(ValueError)
def _err(e):
    return jsonify(error=str(e)), 400


@bp.post("/expenses")
def crear():
    d = request.get_json(force=True)
    g = es.create_expense(_uid(), d.get("amount"), d.get("category"),
                          d.get("date"), d.get("description", ""))
    return jsonify(_ser(g)), 201


@bp.get("/expenses")
def listar():
    a = request.args
    gastos = es.filter_expenses(_uid(), a.get("start"), a.get("end"),
                                a.get("category"))
    return jsonify([_ser(g) for g in gastos])


@bp.put("/expenses/<int:eid>")
def editar(eid):
    g = es.update_expense(_uid(), eid, request.get_json(force=True))
    return (jsonify(_ser(g)), 200) if g else (jsonify(error="No encontrado"), 404)


@bp.delete("/expenses/<int:eid>")
def borrar(eid):
    ok = es.delete_expense(_uid(), eid)
    return ("", 204) if ok else (jsonify(error="No encontrado"), 404)


@bp.get("/stats/summary")
def resumen():
    return jsonify(st.summary(_uid()))


@bp.get("/stats/categories")
def categorias():
    s = date.fromisoformat(request.args["start"])
    e = date.fromisoformat(request.args["end"])
    return jsonify(st.chart_by_category(_uid(), s, e))


@bp.get("/stats/compare")
def comparar():
    f = lambda k: date.fromisoformat(request.args[k])
    return jsonify(st.compare_periods(_uid(), f("a_start"), f("a_end"),
    f("b_start"), f("b_end")))


@bp.get("/stats/monthly")
def mensual():
    n = max(1, min(request.args.get("months", 6, type=int), 12))
    return jsonify(st.monthly_totals(_uid(), n))
