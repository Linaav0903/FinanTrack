/* Presupuesto: límites mensuales por categoría o total */
const TEXTO_ESTADO = { ok: "Dentro del límite", warning: "Cerca del límite", over: "Límite superado" };

async function cargar() {
  const caja = $("budgets");
  try {
    const lista = await api("/api/budgets");
    if (!lista.length) return vacio(caja, "Aún no tienes límites. Define el primero arriba.");
    caja.replaceChildren();
    lista.forEach((b) => {
      const m = el("div", "meter");
      const top = el("div", "meter-top");
      const izq = el("span", "", b.label + " ");
      izq.appendChild(el("span", "chip " + b.state, TEXTO_ESTADO[b.state]));
      top.append(izq, el("span", "", `${dinero(b.spent)} de ${dinero(b.limit)}`));

      const pie = el("div", "meter-top");
      const nota = b.state === "over" ? `Te pasaste por ${dinero(-b.remaining)}` : `Te quedan ${dinero(b.remaining)}`;
      const del = el("button", "btn btn-danger btn-sm", "Quitar límite"); del.type = "button";
      del.addEventListener("click", async () => {
        if (!confirm(`¿Quitar el límite de "${b.label}"?`)) return;
        try { await api(`/api/budgets/${b.id}`, { method: "DELETE" }); await cargar(); }
        catch (e) { $("msg").textContent = e.message; }
      });
      pie.append(el("small", "", `${nota} (${b.percentage}% usado)`), del);

      m.append(top, barra(b.percentage, b.state), pie);
      caja.appendChild(m);
    });
  } catch (e) { vacio(caja, e.message); }
}

$("form-presupuesto").addEventListener("submit", async (e) => {
  e.preventDefault(); $("msg").textContent = "";
  try {
    await api("/api/budgets", enviar("POST", { category: $("b-category").value, amount: $("b-amount").value }));
    e.target.reset();
    await cargar();
  } catch (err) { $("msg").textContent = err.message; }
});

llenarCategorias();
cargar();
