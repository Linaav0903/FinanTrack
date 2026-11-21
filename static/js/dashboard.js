/* Panel principal */
const ESTADO_TEXTO = { ok: "Dentro del límite", warning: "Cerca del límite", over: "Límite superado" };

function conError(contenedor, e) { vacio(contenedor, e.message); }

async function cargarMes() {
  const [ini, fin] = rangoMes();
  const grafica = $("expense-chart"), recientes = $("recent-expenses");
  try {
    const [s, c, g] = await Promise.all([
      api("/api/stats/summary"),
      api(`/api/stats/categories?start=${ini}&end=${fin}`),
      api(`/api/expenses?start=${ini}&end=${fin}`),
    ]);

    $("s-month").textContent = dinero(s.month);
    $("s-mov").textContent = s.movements_month;
    $("s-top").textContent = c.labels[0] || "Sin datos";
    $("s-top-amount").textContent = c.labels.length ? dinero(c.values[0]) + " este mes" : "Registra un gasto para verla";

    if (c.labels.length && graficaDisponible(grafica)) {
      grafica.replaceChildren(document.createElement("canvas"));
      new Chart(grafica.firstChild, {
        type: "doughnut",
        data: { labels: c.labels, datasets: [{ data: c.values, backgroundColor: COLORES, borderWidth: 2, borderColor: "#fff" }] },
        options: {
          maintainAspectRatio: false, cutout: "62%",
          plugins: {
            legend: { position: "right", labels: { boxWidth: 12, font: { size: 13 } } },
            tooltip: { callbacks: { label: (x) => ` ${x.label}: ${dinero(x.parsed)}` } },
          },
        },
      });
    } else if (!c.labels.length) {
      vacio(grafica, "Aún no hay gastos este mes.");
    }

    if (g.length) {
      recientes.replaceChildren();
      g.slice(0, 5).forEach((x) => {
        const fila = el("div", "item");
        const izq = el("div", "", x.category);
        izq.appendChild(el("small", "", fechaCorta(x.date) + (x.description ? " · " + x.description : "")));
        fila.append(izq, el("strong", "", dinero(x.amount)));
        recientes.appendChild(fila);
      });
    }
  } catch (e) { conError(grafica, e); }
}

async function cargarMeses() {
  const caja = $("monthly-chart");
  try {
    const d = await api("/api/stats/monthly?months=6");
    if (!graficaDisponible(caja)) return;
    caja.replaceChildren(document.createElement("canvas"));
    const ultimo = d.values.length - 1;
    new Chart(caja.firstChild, {
      type: "bar",
      data: {
        labels: d.labels,
        datasets: [{ data: d.values, borderRadius: 6,
          backgroundColor: d.values.map((_, i) => (i === ultimo ? "#0C7F60" : "#B8C4D6")) }],
      },
      options: {
        maintainAspectRatio: false,
        plugins: { legend: { display: false }, tooltip: { callbacks: { label: (x) => " " + dinero(x.parsed.y) } } },
        scales: { y: { beginAtZero: true, ticks: { callback: (v) => "$" + v.toLocaleString("es-MX") } }, x: { grid: { display: false } } },
      },
    });
  } catch (e) { conError(caja, e); }
}

async function cargarComparacion(modo) {
  const caja = $("compare-box");
  const semana = modo === "week";
  const [a0, a1] = semana ? rangoSemana(-1) : rangoMes(-1);
  const [b0, b1] = semana ? rangoSemana(0) : rangoMes(0);
  try {
    const r = await api("/api/stats/compare?" + new URLSearchParams({ a_start: a0, a_end: a1, b_start: b0, b_end: b1 }));
    const pasado = semana ? "Semana pasada" : "Mes pasado";
    const actual = semana ? "Esta semana" : "Este mes";

    const grid = el("div", "compare");
    [[pasado, dinero(r.period_a), ""], [actual, dinero(r.period_b), ""],
     ["Diferencia", (r.difference > 0 ? "+" : "") + dinero(r.difference), r.difference > 0 ? "up" : r.difference < 0 ? "down" : ""]]
      .forEach(([k, v, cls]) => {
        const d = el("div"); d.append(el("span", "", k), el("strong", cls, v)); grid.appendChild(d);
      });

    let texto;
    if (r.percentage === null) texto = r.period_b > 0 ? `No hubo gastos ${semana ? "la semana pasada" : "el mes pasado"} para comparar.` : "Aún no hay gastos en ninguno de los dos periodos.";
    else if (r.percentage === 0) texto = "Gastas lo mismo que en el periodo anterior.";
    else texto = `${r.percentage > 0 ? "Subió" : "Bajó"} ${Math.abs(r.percentage)}% ${semana ? "frente a la semana pasada" : "frente al mes pasado"}.`;

    caja.replaceChildren(grid, el("p", "", texto));
    const cambios = r.by_category.filter((x) => x.difference !== 0).slice(0, 4);
    if (cambios.length) {
      const lista = el("div", "diff-list"); lista.style.marginTop = "14px";
      cambios.forEach((x) => {
        const f = el("div"); f.append(el("span", "", x.category),
          el("strong", x.difference > 0 ? "up" : "down", (x.difference > 0 ? "+" : "") + dinero(x.difference)));
        lista.appendChild(f);
      });
      caja.appendChild(lista);
    }

    if (!semana) {
      const d = $("s-delta"); d.replaceChildren();
      if (r.percentage === null) d.textContent = "Sin gastos el mes pasado para comparar";
      else {
        d.append(el("span", r.percentage > 0 ? "up" : "down", (r.percentage > 0 ? "↑ " : r.percentage < 0 ? "↓ " : "") + Math.abs(r.percentage) + "%"), " frente al mes pasado");
      }
    }
  } catch (e) { conError(caja, e); }
}

async function cargarPresupuestos() {
  const caja = $("budget-list");
  try {
    const lista = await api("/api/budgets");
    if (!lista.length) return vacio(caja, "Aún no defines límites. Crea uno en Presupuesto.");
    caja.replaceChildren();
    lista.slice(0, 4).forEach((b) => {
      const m = el("div", "meter");
      const top = el("div", "meter-top");
      top.append(el("span", "", b.label), el("span", "", `${dinero(b.spent)} de ${dinero(b.limit)}`));
      const nota = b.state === "over" ? `Te pasaste por ${dinero(-b.remaining)}` : `Te quedan ${dinero(b.remaining)}`;
      m.append(top, barra(b.percentage, b.state), el("small", "", `${nota} · ${ESTADO_TEXTO[b.state]}`));
      caja.appendChild(m);
    });
  } catch (e) { conError(caja, e); }
}

async function cargarMetas() {
  const caja = $("goal-list");
  try {
    const [metas, r] = await Promise.all([api("/api/savings/goals"), api("/api/savings/summary")]);
    $("s-saved").textContent = dinero(r.total_saved);
    $("s-goals").textContent = r.goals_count
      ? `${r.goals_count} ${r.goals_count === 1 ? "meta" : "metas"}, ${r.completed_count} ${r.completed_count === 1 ? "cumplida" : "cumplidas"}`
      : "Aún no tienes metas";
    if (!metas.length) return vacio(caja, "Aún no tienes metas. Crea la primera en Ahorro.");
    caja.replaceChildren();
    metas.slice(0, 4).forEach((g) => {
      const m = el("div", "meter");
      const top = el("div", "meter-top");
      top.append(el("span", "", g.name), el("span", "", `${dinero(g.saved)} de ${dinero(g.target)}`));
      m.append(top, barra(g.percentage), el("small", "", g.completed ? "Meta cumplida" : `${g.percentage}% · faltan ${dinero(g.remaining)}`));
      caja.appendChild(m);
    });
  } catch (e) { conError(caja, e); }
}

function modo(m) {
  $("cmp-week").classList.toggle("on", m === "week");
  $("cmp-month").classList.toggle("on", m === "month");
  cargarComparacion(m);
}
$("cmp-week").addEventListener("click", () => modo("week"));
$("cmp-month").addEventListener("click", () => modo("month"));

cargarMes(); cargarMeses(); cargarComparacion("month"); cargarPresupuestos(); cargarMetas();
