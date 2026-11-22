import csv
import io
from datetime import datetime
from decimal import Decimal, InvalidOperation
from flask import(Blueprint,jsonify, request, session, Response
)
from models import db, Expense
from datetime import date
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

@bp.get("/expenses/export-csv")
def exportar_csv():
    user_id = _uid()

    # Obtener los filtros enviados desde la página
    fecha_inicio = request.args.get("start", "")
    fecha_fin = request.args.get("end", "")
    categoria = request.args.get("category", "").strip()

    # Validar las fechas recibidas
    try:
        inicio = date.fromisoformat(fecha_inicio) if fecha_inicio else None
        fin = date.fromisoformat(fecha_fin) if fecha_fin else None
    except ValueError:
        return jsonify(error="Formato de fecha inválido"), 400

    if inicio and fin and inicio > fin:
        return jsonify(error="La fecha inicial es posterior a la final"), 400

    # Consultar solo los gastos del usuario
    consulta = Expense.query.filter_by(user_id=user_id)

    # Aplicar los filtros seleccionados
    if inicio:
        consulta = consulta.filter(Expense.date >= inicio)

    if fin:
        consulta = consulta.filter(Expense.date <= fin)

    if categoria and categoria.lower() != "todas":
        consulta = consulta.filter(
            Expense.category.ilike(categoria)
        )

    gastos = consulta.order_by(
        Expense.date.desc(),
        Expense.id.desc()
    ).all()

    # Generar el archivo CSV
    archivo = io.StringIO()
    archivo.write("\ufeff")

    escritor = csv.writer(archivo)
    escritor.writerow([
        "Fecha", "Categoria", "Importe", "Descripcion"
    ])

    for gasto in gastos:
        escritor.writerow([
            gasto.date.isoformat(),
            gasto.category,
            f"{gasto.amount:.2f}",
            gasto.description or ""
        ])

    nombre = "finantrack_gastos_" + datetime.now().strftime("%Y%m%d") + ".csv"

    return Response(
        archivo.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{nombre}"',
            "Cache-Control": "no-store"
        }
    )

@bp.post("/expenses/import-csv")
def importar_csv():
    archivo = request.files.get("archivo")

    if archivo is None or not archivo.filename:
        return jsonify(error="Selecciona un archivo CSV."), 400

    if not archivo.filename.lower().endswith(".csv"):
        return jsonify(error="Solo se permiten archivos CSV."), 400

    # Máximo 2 MB
    contenido = archivo.read(2 * 1024 * 1024 + 1)

    if len(contenido) > 2 * 1024 * 1024:
        return jsonify(error="El archivo supera los 2 MB."), 400

    try:
        texto = contenido.decode("utf-8-sig")
    except UnicodeDecodeError:
        return jsonify(error="El archivo debe estar en UTF-8."), 400

    try:
        lector = csv.DictReader(io.StringIO(texto))

        columnas = {"Fecha", "Categoria", "Importe", "Descripcion"}

        if lector.fieldnames is None or set(lector.fieldnames) != columnas:
            return jsonify(
                error="El CSV debe contener: Fecha, Categoria, Importe y Descripcion."
            ), 400

        validos = []
        errores = []
        rechazados = 0

        for numero, fila in enumerate(lector, start=2):
            try:
                if None in fila or any(valor is None for valor in fila.values()):
                    raise ValueError("Número de columnas incorrecto")

                fecha = date.fromisoformat(fila["Fecha"].strip())
                categoria = fila["Categoria"].strip()
                importe = Decimal(fila["Importe"].strip())
                descripcion = fila["Descripcion"].strip()

                if not importe.is_finite() or importe <= 0:
                    raise ValueError("El importe debe ser positivo")

                if importe > Decimal("99999999.99"):
                    raise ValueError("Importe demasiado grande")

                if importe.as_tuple().exponent < -2:
                    raise ValueError("Máximo dos decimales")

                if not categoria or len(categoria) > 50:
                    raise ValueError("Categoría inválida")

                if len(descripcion) > 200:
                    raise ValueError("Descripción demasiado larga")

                validos.append(Expense(
                    user_id=_uid(),
                    amount=importe,
                    category=categoria,
                    date=fecha,
                    description=descripcion
                ))

            except (ValueError, InvalidOperation, TypeError) as error:
                rechazados += 1
                errores.append(f"Fila {numero}: {error}")

    except csv.Error:
        return jsonify(error="El archivo CSV tiene un formato inválido."), 400

    try:
        db.session.add_all(validos)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify(error="No se pudieron guardar los gastos."), 500

    return jsonify(
        importados=len(validos),
        rechazados=rechazados,
        errores=errores[:20]
    ), 200
