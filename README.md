# FinanTrack

Sistema web de control de gastos y ahorro personal. Permite registrar gastos,
fijar presupuestos mensuales, crear metas de ahorro y ver estadísticas.

**Tecnologías:** Python, Flask, SQLite (SQLAlchemy), Chart.js, HTML/CSS/JS.

## Funciones

- Registro e inicio de sesión de usuarios (contraseñas cifradas).
- Gastos: crear, editar, eliminar y filtrar por fechas y categoría.
- Panel con totales, gasto por categoría, últimos 6 meses y comparación
  de semanas y meses.
- Presupuesto mensual por categoría o total, con avisos al acercarse al límite.
- Metas de ahorro con abonos y barra de progreso.

Abre http://127.0.0.1:5000 en el navegador. La base de datos (`database.db`)
se crea sola la primera vez.

### Datos de demostración (opcional)

```bash
py seed.py
```

Crea una cuenta de prueba con gastos, presupuestos y metas de ejemplo:

- Correo: `demo@finantrack.com`
- Contraseña: `demo1234`

Para empezar sin datos, borra `database.db` y vuelve a iniciar la app.

## Pruebas

```bash
py -m pytest -v
```

## Estructura

```
FinanTrack/
├── app.py                  # Aplicación Flask, páginas y autenticación
├── models.py               # Tablas de la base de datos
├── seed.py                 # Datos de demostración
├── routes/                 # API (JSON): gastos, ahorro, presupuestos
├── services/               # Lógica de negocio y cálculos
├── templates/              # Páginas HTML
├── static/                 # CSS y JavaScript
└── tests/                  # Pruebas automáticas (pytest)
```

## Base de datos

| Tabla | Contenido |
| --- | --- |
| `users` | Usuarios y contraseñas cifradas |
| `expenses` | Gastos de cada usuario |
| `savings_goals` | Metas de ahorro |
| `savings_deposits` | Abonos a las metas |
| `budgets` | Límites mensuales |

Todas las consultas filtran por el usuario que inició sesión.

## Flujo de trabajo en equipo

- Cada integrante trabaja en su propia rama (`git checkout -b nombre-rama`).
- Los cambios se unen a `main` mediante Pull Request, revisado por otra persona.
- Antes de empezar a trabajar: `git pull`.
- No subir `database.db`, `venv/` ni `.env` (ya están en `.gitignore`).

## Integrantes

- Integrante 1: base de datos, autenticación y seguridad
- Integrante 2: lógica de negocio y estadísticas
- Integrante 3: interfaz, gráficas y CSV
