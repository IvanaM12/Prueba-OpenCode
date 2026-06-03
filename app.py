from flask import Flask, render_template_string, request, redirect, url_for

from services.almacenamiento import cargar_libros, guardar_libros
from models.libro import Libro

app = Flask(__name__)

# Minimal inline template to keep changes small (no templates folder yet)
INDEX_HTML = """
<!doctype html>
<html lang=\"es\">
<head>
  <meta charset=\"utf-8\" />
  <title>Biblioteca</title>
  <style>
    :root {
      --bg: #0f172a;           /* slate-900 */
      --panel: #111827;        /* gray-900 */
      --border: #1f2937;       /* gray-800 */
      --text: #e5e7eb;         /* gray-200 */
      --muted: #94a3b8;        /* slate-400 */
      --primary: #2563eb;      /* blue-600 */
      --primary-2: #3b82f6;    /* blue-500 */
      --accent: #38bdf8;       /* sky-400 */
      --danger: #ef4444;       /* red-500 */
    }

    * { box-sizing: border-box; }
    body {
      font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
      margin: 0;
      background: radial-gradient(1200px 600px at 10% -10%, #1d4ed8 0%, transparent 60%), var(--bg);
      color: var(--text);
    }

    .container { max-width: 1000px; margin: 24px auto; padding: 16px; }

    h1 { margin: 0 0 16px; font-weight: 700; letter-spacing: .3px; }
    h2 { margin: 20px 0 10px; color: var(--muted); font-weight: 600; }

    .card {
      background: linear-gradient(180deg, rgba(37,99,235,0.08), rgba(0,0,0,0)) , var(--panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px;
      box-shadow: 0 10px 30px rgba(0,0,0,.25);
    }

    form { display: grid; grid-template-columns: repeat(6, 1fr); gap: 8px; }
    input {
      grid-column: span 1;
      padding: 10px 12px;
      border-radius: 10px;
      border: 1px solid var(--border);
      background: #020617;
      color: var(--text);
      outline: none;
    }
    input::placeholder { color: #64748b; }
    input:focus { border-color: var(--primary-2); box-shadow: 0 0 0 2px rgba(59,130,246,.2); }

    .span-2 { grid-column: span 2; }
    .span-3 { grid-column: span 3; }

    button {
      grid-column: span 1;
      padding: 10px 12px;
      border-radius: 10px;
      border: 1px solid rgba(59,130,246,.4);
      background: linear-gradient(180deg, var(--primary-2), var(--primary));
      color: white;
      cursor: pointer;
      transition: transform .05s ease, box-shadow .15s ease;
      box-shadow: 0 6px 16px rgba(37,99,235,.35);
    }
    button:hover { box-shadow: 0 10px 24px rgba(37,99,235,.45); }
    button:active { transform: translateY(1px); }

    .error {
      margin-top: 10px;
      padding: 10px 12px;
      border-radius: 10px;
      background: rgba(239,68,68,.12);
      border: 1px solid rgba(239,68,68,.4);
      color: #fecaca;
    }

    table { width: 100%; border-collapse: collapse; margin-top: 12px; }
    th, td { padding: 10px; border-bottom: 1px solid var(--border); }
    th { text-align: left; color: var(--muted); font-weight: 600; }

    tr { background: transparent; }
    tr:hover { background: rgba(56,189,248,.06); }

    .pending { color: var(--accent); }

    a {
      color: #93c5fd;
      text-decoration: none;
      border: 1px solid rgba(147,197,253,.3);
      padding: 6px 10px;
      border-radius: 8px;
    }
    a:hover { background: rgba(147,197,253,.12); }

    .header {
      display: flex; align-items: center; justify-content: space-between; gap: 12px;
      margin-bottom: 12px;
    }

    .badge {
      padding: 4px 8px; border-radius: 999px; font-size: 12px; border: 1px solid var(--border);
      color: var(--muted);
    }
  </style>
</head>
<body>
  <div class=\"container\">
    <div class=\"header\">
      <h1>📚 Biblioteca</h1>
      <span class=\"badge\">Modo web</span>
    </div>

    <div class=\"card\">
      <h2>Añadir libro</h2>
      <form method=\"post\" action=\"/add\">
        <input class=\"span-3\" name=\"titulo\" placeholder=\"Título\" required />
        <input class=\"span-3\" name=\"autor\" placeholder=\"Autor (opcional)\" />
        <input class=\"span-2\" name=\"isbn\" placeholder=\"ISBN\" required />
        <input class=\"span-2\" name=\"genero\" placeholder=\"Género\" />
        <input class=\"span-1\" name=\"anio\" type=\"number\" placeholder=\"Año\" required />
        <input class=\"span-1\" name=\"paginas\" type=\"number\" placeholder=\"Páginas\" required />
        <button class=\"span-1\" type=\"submit\">Añadir</button>
      </form>

      {% if error %}
        <div class=\"error\">{{ error }}</div>
      {% endif %}
    </div>

    <div class=\"card\" style=\"margin-top:16px\">
      <h2>Libros</h2>
      <table>
        <tr>
          <th>Título</th><th>Autor</th><th>Año</th><th>Páginas</th><th>Estado</th><th>Acciones</th>
        </tr>
        {% for l in libros %}
        <tr class=\"{{ 'pending' if not l.leido else '' }}\">
          <td>{{ l.titulo }}</td>
          <td>{{ l.autor }}</td>
          <td>{{ l.anio }}</td>
          <td>{{ l.paginas }}</td>
          <td>{{ 'Leído' if l.leido else 'Pendiente' }}</td>
          <td>
            <a href=\"/delete/{{ l.isbn }}\">Eliminar</a>
          </td>
        </tr>
        {% endfor %}
      </table>
    </div>
  </div>
</body>
</html>
"""


@app.route("/")
def index():
    libros = cargar_libros()
    return render_template_string(INDEX_HTML, libros=libros, error=None)


@app.route("/add", methods=["POST"])
def add():
    libros = cargar_libros()
    data = request.form

    try:
        libro = Libro(
            titulo=data.get("titulo", ""),
            autor=data.get("autor", ""),
            isbn=data.get("isbn", ""),
            genero=data.get("genero", ""),
            anio=int(data.get("anio", 0)),
            paginas=int(data.get("paginas", 0)),
        )
        libros.append(libro)
        guardar_libros(libros)
        return redirect(url_for("index"))
    except Exception as e:
        # Render same page with error message
        return render_template_string(INDEX_HTML, libros=libros, error=str(e))


@app.route("/delete/<isbn>")
def delete(isbn):
    libros = cargar_libros()
    libros = [l for l in libros if l.isbn != isbn]
    guardar_libros(libros)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
