/* Ahorro: metas, abonos y gráfica mensual */
let graficaAhorro;

function tarjetaMeta(g) {
  const card = el("article", "goal");
  const top = el("div", "goal-top");
  top.append(el("h3", "", g.name), el("span", "chip " + (g.completed ? "ok" : ""), g.completed ? "Cumplida" : g.percentage + "%"));

  const fig = el("p", "figures");
  fig.append(el("strong", "num", dinero(g.saved)), " de " + dinero(g.target));

  const nota = g.completed ? "Meta alcanzada"
    : `Faltan ${dinero(g.remaining)}` + (g.deadline ? ` · fecha límite ${fechaCorta(g.deadline)}` : "");
  card.append(top, fig, barra(g.percentage), el("small", g.completed ? "done-note" : "figures", nota));

  if (!g.completed) {
    const f = document.createElement("form");
    const i = document.createElement("input");
    i.type = "number"; i.step = "0.01"; i.min = "0.01"; i.required = true; i.placeholder = "Monto a abonar";
    i.setAttribute("aria-label", "Monto a abonar a " + g.name);
    const b = el("button", "btn btn-primary btn-sm", "Abonar"); b.type = "submit";
    f.append(i, b);
    f.addEventListener("submit", async (e) => {
      e.preventDefault(); $("msg").textContent = "";
      try { await api(`/api/savings/goals/${g.id}/deposits`, enviar("POST", { amount: i.value })); await cargarTodo(); }
      catch (err) { $("msg").textContent = err.message; }
    });
    card.appendChild(f);
  }

  const del = el("button", "btn btn-danger btn-sm", "Eliminar meta"); del.type = "button";
  del.style.justifySelf = "start";
  del.addEventListener("click", async () => {
    if (!confirm(`¿Eliminar la meta "${g.name}" y sus abonos?`)) return;
    try { await api(`/api/savings/goals/${g.id}`, { method: "DELETE" }); await cargarTodo(); }
    catch (err) { $("msg").textContent = err.message; }
  });
  card.appendChild(del);
  return card;
}

async function cargarTodo() {
  const caja = $("goals"), graf = $("savings-chart");
  try {
    const [metas, r] = await Promise.all([api("/api/savings/goals"), api("/api/savings/summary")]);
    $("a-total").textContent = dinero(r.total_saved);
    $("a-count").textContent = r.goals_count;
    $("a-done").textContent = r.completed_count;

    if (!metas.length) vacio(caja, "Aún no tienes metas. Crea la primera con el formulario de arriba.");
    else { caja.replaceChildren(); metas.forEach((g) => caja.appendChild(tarjetaMeta(g))); }

    if (!graficaDisponible(graf)) return;
    if (graficaAhorro) graficaAhorro.destroy();
    graf.replaceChildren(document.createElement("canvas"));
    const ult = r.monthly.values.length - 1;
    graficaAhorro = new Chart(graf.firstChild, {
      type: "bar",
      data: { labels: r.monthly.labels, datasets: [{ data: r.monthly.values, borderRadius: 6,
        backgroundColor: r.monthly.values.map((_, i) => (i === ult ? "#0C7F60" : "#B8C4D6")) }] },
      options: {
        maintainAspectRatio: false,
        plugins: { legend: { display: false }, tooltip: { callbacks: { label: (x) => " " + dinero(x.parsed.y) } } },
        scales: { y: { beginAtZero: true, ticks: { callback: (v) => "$" + v.toLocaleString("es-MX") } }, x: { grid: { display: false } } },
      },
    });
  } catch (e) { vacio(caja, e.message); }
}

$("form-meta").addEventListener("submit", async (e) => {
  e.preventDefault(); $("msg").textContent = "";
  try {
    await api("/api/savings/goals", enviar("POST", { name: $("g-name").value, target: $("g-target").value, deadline: $("g-deadline").value }));
    e.target.reset();
    await cargarTodo();
  } catch (err) { $("msg").textContent = err.message; }
});

cargarTodo();
