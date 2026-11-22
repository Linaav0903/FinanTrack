/* Mis gastos: alta, edición, filtros y borrado */
let editando = null;

function hoy() { return iso(new Date()); }

function salirDeEdicion() {
  editando = null;
  $("form-title").textContent = "Nuevo gasto";
  $("btn-guardar").textContent = "Guardar gasto";
  $("btn-cancelar").hidden = true;
  $("amount").value = ""; $("category").value = ""; $("description").value = "";
  $("date").value = hoy();
}

function empezarEdicion(g) {
  editando = g.id;
  $("form-title").textContent = "Editar gasto";
  $("btn-guardar").textContent = "Guardar cambios";
  $("btn-cancelar").hidden = false;
  $("amount").value = g.amount; $("category").value = g.category;
  $("date").value = g.date; $("description").value = g.description || "";
  $("msg").textContent = "";
  window.scrollTo({ top: 0, behavior: "smooth" });
  $("amount").focus();
}

async function cargarLista() {
  const p = new URLSearchParams();
  if ($("f-start").value) p.set("start", $("f-start").value);
  if ($("f-end").value) p.set("end", $("f-end").value);
  if ($("f-cat").value.trim()) p.set("category", $("f-cat").value.trim());

  const gastos = await api("/api/expenses?" + p);
  const tbody = $("lista");
  tbody.replaceChildren();
  $("vacio").hidden = gastos.length > 0;

  gastos.forEach((g) => {
    const tr = document.createElement("tr");
    const celdaCat = el("td"); celdaCat.appendChild(el("span", "chip", g.category));
    tr.append(el("td", "", fechaCorta(g.date)), celdaCat, el("td", "", g.description || ""), el("td", "r", dinero(g.amount)));

    const acc = el("td", "acciones");
    const ed = el("button", "btn btn-ghost btn-sm", "Editar"); ed.type = "button";
    ed.addEventListener("click", () => empezarEdicion(g));
    const del = el("button", "btn btn-danger btn-sm", "Eliminar"); del.type = "button";
    del.addEventListener("click", async () => {
      if (!confirm("¿Eliminar este gasto?")) return;
      try { await api(`/api/expenses/${g.id}`, { method: "DELETE" }); if (editando === g.id) salirDeEdicion(); await cargarLista(); }
      catch (e) { $("msg").textContent = e.message; }
    });
    acc.append(ed, " ", del);
    tr.appendChild(acc);
    tbody.appendChild(tr);
  });

  const total = gastos.reduce((s, g) => s + Number(g.amount), 0);
  $("total").textContent = dinero(total);
  $("conteo").textContent = `${gastos.length} ${gastos.length === 1 ? "gasto" : "gastos"}`;
}

const recargar = () => cargarLista().catch((e) => { $("msg").textContent = e.message; });

$("form-gasto").addEventListener("submit", async (e) => {
  e.preventDefault();
  $("msg").textContent = "";
  const datos = { amount: $("amount").value, category: $("category").value,
                  date: $("date").value, description: $("description").value };
  try {
    if (editando) await api(`/api/expenses/${editando}`, enviar("PUT", datos));
    else await api("/api/expenses", enviar("POST", datos));
    salirDeEdicion();
    await cargarLista();
  } catch (err) { $("msg").textContent = err.message; }
});
const btnExportarCSV = document.getElementById("btn-exportar-csv");

if (btnExportarCSV) {
    btnExportarCSV.addEventListener("click", function (evento) {
        evento.preventDefault();

        const inicio = document.getElementById("f-start").value;
        const fin = document.getElementById("f-end").value;
        const categoria = document.getElementById("f-cat").value.trim();

        if (inicio && fin && inicio > fin) {
            alert("La fecha inicial no puede ser posterior a la final.");
            return;
        }

        const url = new URL(btnExportarCSV.href);

        if (inicio) {
            url.searchParams.set("start", inicio);
        }

        if (fin) {
            url.searchParams.set("end", fin);
        }

        if (categoria && categoria.toLowerCase() !== "todas") {
            url.searchParams.set("category", categoria);
        }

        window.location.href = url.toString();
    });
}

$("btn-cancelar").addEventListener("click", salirDeEdicion);
$("f-btn").addEventListener("click", recargar);
$("f-clear").addEventListener("click", () => { ["f-start", "f-end", "f-cat"].forEach((i) => { $(i).value = ""; }); recargar(); });

llenarCategorias();
salirDeEdicion();
recargar();

$("form-importar-csv").addEventListener("submit", async (e) => {
    e.preventDefault();

    const archivo = $("archivo-csv").files[0];
    const mensaje = $("msg-importar");
    const boton = $("btn-importar-csv");

    mensaje.textContent = "";

    if (!archivo) {
        mensaje.textContent = "Selecciona un archivo CSV.";
        return;
    }

    if (!archivo.name.toLowerCase().endsWith(".csv")) {
        mensaje.textContent = "El archivo debe tener extensión .csv.";
        return;
    }

    const datos = new FormData();
    datos.append("archivo", archivo);

    boton.disabled = true;
    boton.textContent = "Importando...";

    try {
        const respuesta = await fetch("/api/expenses/import-csv", {
            method: "POST",
            body: datos
        });

        if (respuesta.status === 401) {
            window.location.href = "/login";
            return;
        }

        const resultado = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(resultado.error || "No se pudo importar el archivo.");
        }

        mensaje.textContent =
            `Se importaron ${resultado.importados} gastos. ` +
            `${resultado.rechazados} filas rechazadas.` +
            (resultado.errores.length
                ? " Detalles: " + resultado.errores.join(" | ")
                : "");

        $("form-importar-csv").reset();

        // Limpiar filtros para mostrar todos los gastos importados
        ["f-start", "f-end", "f-cat"].forEach((id) => {
            $(id).value = "";
        });

        await cargarLista();

    } catch (error) {
        mensaje.textContent = error.message;
    } finally {
        boton.disabled = false;
        boton.textContent = "Importar gastos";
    }
});