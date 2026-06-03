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
    h2 { margin: 20px 0 10px; color: var(--ink); font-weight: 600; }

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
      background: var(--muted);
      color: var(--ink);
      cursor: pointer;
      transition: transform .05s ease, box-shadow .15s ease;
      box-shadow: 0 6px 16px gray;
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
    .stars { color: #fbbf24; }
    :root {
      --bg: #f4ecd8;          /* paper */
      --card: #fbf6e8;        /* parchment */
      --ink: #3b2f2f;         /* brown ink */
      --muted: #e7dcc2;       /* light paper */
      --border: #c9b48a;      /* aged border */
      --accent: #7c5a2b;      /* leather */
      --accent-2: #a67c52;    /* wood */
    }
    .actions { display: flex; gap: 8px; }
    body { background: var(--bg); color: var(--ink); font-family: Georgia, 'Times New Roman', serif; }
    .container { max-width: 1000px; margin: 28px auto; padding: 0 16px; }
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 6px; padding: 18px; box-shadow: 0 2px 6px rgba(0,0,0,0.08); }
    h1 { font-size: 26px; margin-bottom: 14px; letter-spacing: 0.5px; }
    .btn {
      padding: 6px 10px; border-radius: 4px; text-decoration: none;
      background: var(--muted); color: var(--ink); border: 1px solid var(--border);
      font-size: 12px;
    }
    .btn:hover { background: #efe4c9; }
    .btn.primary { background: var(--accent); color: #fff; border: 1px solid #6b4f24; }
    .btn.danger { background: #8b0000; color: #fff; border: none; }

    .rating {
      display: flex;
      gap: 4px;
      font-size: 18px;
      cursor: pointer;
    }
    .rating input { display: none; }
    .rating label { color: #c7d2fe; }
    .rating input:checked ~ label { color: #fbbf24; }
    .rating label:hover,
    .rating label:hover ~ label { color: #fbbf24; }

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
      color: var(--ink);
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
      <h2>{{ 'Editar libro' if edit else 'Añadir libro' }}</h2>
      <form method=\"post\" action=\"{{ '/edit/' + edit.isbn if edit else '/add' }}\">
        <input class=\"span-3\" name=\"titulo\" placeholder=\"Título\" value=\"{{ edit.titulo if edit else '' }}\" required />
        <input class=\"span-3\" name=\"autor\" placeholder=\"Autor (opcional)\" value=\"{{ edit.autor if edit else '' }}\" />
        <input class=\"span-2\" name=\"isbn\" placeholder=\"ISBN\" value=\"{{ edit.isbn if edit else '' }}\" {{ 'readonly' if edit else '' }} required />
        <input class=\"span-2\" name=\"genero\" placeholder=\"Género\" value=\"{{ edit.genero if edit else '' }}\" />
        <input class=\"span-1\" name=\"anio\" type=\"number\" placeholder=\"Año\" value=\"{{ edit.anio if edit else '' }}\" required />
        <input class=\"span-1\" name=\"paginas\" type=\"number\" placeholder=\"Páginas\" value=\"{{ edit.paginas if edit else '' }}\" required />
        <div class=\"span-2 rating\">
          {% for i in range(5,0,-1) %}
            <input type=\"radio\" id=\"star{{i}}\" name=\"valoracion\" value=\"{{i}}\" {{ 'checked' if edit and edit.valoracion == i else '' }} />
            <label for=\"star{{i}}\">★</label>
          {% endfor %}
        </div>
        <button class=\"span-1\" type=\"submit\">{{ 'Guardar' if edit else 'Añadir' }}</button>
      </form>

  {% if error %}
        <div class=\"error\">{{ error }}</div>
      {% endif %}
    </div>

    <div class=\"card\" style=\"margin-top:16px\">
      <h2>Libros</h2>
      <table style="width:100%; border-collapse: collapse; font-size:14px;">
        <tr>
          <th>Título</th><th>Autor</th><th>Año</th><th>Páginas</th><th>Valoración</th><th>Estado</th><th>Acciones</th>
        </tr>
        {% for l in libros %}
        <tr class=\"{{ 'pending' if not l.leido else '' }}\" style="border-top:1px solid var(--border);">
          <td style="font-weight:600;">{{ l.titulo }}</td>
          <td>{{ l.autor }}</td>
          <td>{{ l.anio }}</td>
          <td>{{ l.paginas }}</td>
          <td>
            {% if l.valoracion %}
              <span class=\"stars\">{{ '★' * l.valoracion }}{{ '☆' * (5 - l.valoracion) }}</span>
            {% else %}
              -
            {% endif %}
          </td>
          <td>{{ 'Leído' if l.leido else 'Pendiente' }}</td>
          <td>
            <div class=\"actions\">
              {% if not l.leido %}
                <a class=\"btn primary\" href=\"/read/{{ l.isbn }}\">Leído</a>
              {% endif %}
              <a class=\"btn\" href=\"/edit/{{ l.isbn }}\">Editar</a>
              <a class=\"btn danger\" href=\"/delete/{{ l.isbn }}\">Eliminar</a>
            </div>
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
    return render_template_string(INDEX_HTML, libros=libros, error=None, edit=None)


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
        val = data.get("valoracion")
        if val:
            try:
                libro.actualizar_valoracion(int(val))
            except Exception:
                pass
        libros.append(libro)
        guardar_libros(libros)
        return redirect(url_for("index"))
    except Exception as e:
        # Render same page with error message
        return render_template_string(INDEX_HTML, libros=libros, error=str(e), edit=None)


@app.route("/delete/<isbn>")
def delete(isbn):
    libros = cargar_libros()
    libros = [l for l in libros if l.isbn != isbn]
    guardar_libros(libros)
    return redirect(url_for("index"))


@app.route("/read/<isbn>")
def mark_read(isbn):
    libros = cargar_libros()
    for l in libros:
        if l.isbn == isbn:
            # Marca como leído sin valoración (puede editarse luego)
            l.marcar_leido(None, "")
            break
    guardar_libros(libros)
    return redirect(url_for("index"))


@app.route("/edit/<isbn>", methods=["GET", "POST"])
def edit(isbn):
    libros = cargar_libros()
    libro = next((l for l in libros if l.isbn == isbn), None)
    if not libro:
        return redirect(url_for("index"))

    if request.method == "POST":
        data = request.form
        try:
            # Create a new validated instance, then replace fields
            actualizado = Libro(
                titulo=data.get("titulo", ""),
                autor=data.get("autor", ""),
                isbn=libro.isbn,
                genero=data.get("genero", ""),
                anio=int(data.get("anio", 0)),
                paginas=int(data.get("paginas", 0)),
            )

            val = data.get("valoracion")
            if val:
                try:
                    actualizado.actualizar_valoracion(int(val))
                except Exception:
                    pass
            else:
                actualizado.valoracion = None

            # Preserve read-related fields (but keep new valoracion)
            actualizado.leido = libro.leido
            actualizado.fecha_lectura = libro.fecha_lectura
            actualizado.notas = libro.notas

            # Replace in list
            for i, l in enumerate(libros):
                if l.isbn == isbn:
                    libros[i] = actualizado
                    break

            guardar_libros(libros)
            return redirect(url_for("index"))
        except Exception as e:
            return render_template_string(INDEX_HTML, libros=libros, error=str(e), edit=libro)

    # GET: show form prefilled
    return render_template_string(INDEX_HTML, libros=libros, error=None, edit=libro)


if __name__ == "__main__":
    app.run(debug=True)
