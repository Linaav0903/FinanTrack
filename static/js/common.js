/* Utilidades compartidas por todas las páginas de la app */
const $ = (id) => document.getElementById(id);
const pad = (n) => String(n).padStart(2, "0");
const iso = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
const dinero = (n) => Number(n).toLocaleString("es-MX", { style: "currency", currency: "MXN" });
const MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];
const COLORES = ["#2CCB9F", "#1B2B4B", "#E3A21A", "#C93C2F", "#6C8EAD", "#8E6BBF", "#0C7F60", "#B8C4D6"];
const CATEGORIAS = ["Comida", "Transporte", "Escuela", "Entretenimiento", "Salud", "Hogar", "Ropa", "Otros"];

function el(tag, clase, texto) {
  const e = document.createElement(tag);
  if (clase) e.className = clase;
  if (texto !== undefined) e.textContent = texto;
  return e;
}

async function api(url, opts) {
  const r = await fetch(url, opts);
  if (r.status === 401) {
    location.href = "/login";
    throw new Error("Tu sesión expiró. Inicia sesión de nuevo.");
  }
  if (!r.ok) {
    const d = await r.json().catch(() => ({}));
    throw new Error(d.error || "No se pudo completar la solicitud.");
  }
  return r.status === 204 ? null : r.json();
}

const enviar = (metodo, cuerpo) => ({
  method: metodo,
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(cuerpo),
});

function rangoMes(offset = 0) {
  const h = new Date();
  const ini = new Date(h.getFullYear(), h.getMonth() + offset, 1);
  const fin = new Date(ini.getFullYear(), ini.getMonth() + 1, 0);
  return [iso(ini), iso(fin)];
}

function rangoSemana(offset = 0) {
  const h = new Date();
  const lunes = new Date(h.getFullYear(), h.getMonth(), h.getDate() - ((h.getDay() + 6) % 7) + offset * 7);
  const domingo = new Date(lunes.getFullYear(), lunes.getMonth(), lunes.getDate() + 6);
  return [iso(lunes), iso(domingo)];
}

function fechaCorta(s) {
  const [y, m, d] = s.split("-").map(Number);
  return `${d} ${MESES[m - 1]} ${y}`;
}

function barra(pct, estado) {
  const b = el("div", "bar " + (estado || ""));
  b.setAttribute("role", "progressbar");
  b.setAttribute("aria-valuenow", Math.round(pct));
  b.setAttribute("aria-valuemin", "0");
  b.setAttribute("aria-valuemax", "100");
  const i = document.createElement("i");
  i.style.width = Math.max(0, Math.min(pct, 100)) + "%";
  b.appendChild(i);
  return b;
}

function vacio(contenedor, texto) {
  contenedor.replaceChildren(el("p", "empty", texto));
}

function llenarCategorias() {
  const dl = $("categorias");
  if (!dl) return;
  CATEGORIAS.forEach((c) => { const o = document.createElement("option"); o.value = c; dl.appendChild(o); });
}

function graficaDisponible(contenedor) {
  if (typeof Chart !== "undefined") return true;
  vacio(contenedor, "No se pudo cargar la gráfica. Revisa tu conexión a internet.");
  return false;
}
