import sys
import os
from rich.console import Console
from rich.table import Table
import json
from urllib.request import urlopen
from urllib.error import URLError, HTTPError


sys.path.insert(0, os.path.dirname(__file__))
console = Console()

from models.libro import Libro
from services import (
    cargar_libros,
    guardar_libros,
    buscar_por_titulo,
    buscar_por_autor,
    filtrar_por_genero,
    filtrar_leidos,
    filtrar_pendientes,
    filtrar_por_valoracion,
    estadisticas,
)

# ── Utilidades de presentación ──────────────────────────────────────────────

def separador(char="─", ancho=50):
    console.print(char * ancho, style="dim")

def titulo(texto: str):
    separador()
    console.print(f"  {texto}", style="bold cyan")
    separador()

def mostrar_lista(libros: list, encabezado: str = "Resultados"):
    titulo(encabezado)
    if not libros:
        console.print("  No se encontraron libros.", style="yellow")
        return
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", justify="right")
    table.add_column("Libro")
    for i, libro in enumerate(libros, 1):
        table.add_row(str(i), str(libro))
    console.print(table)

def pedir_numero(mensaje: str, minimo: int = 1, maximo: int = 9999) -> int:
    while True:
        try:
            val = int(input(mensaje).strip())
            if minimo <= val <= maximo:
                return val
            print(f"  Introduce un número entre {minimo} y {maximo}.")
        except ValueError:
            print("  Valor no válido.")

def pedir_valoracion() -> int | None:
    """Pide una valoración opcional entre 1 y 5. Enter para omitir."""
    while True:
        try:
            entrada = input("  Valoración (1-5, Enter para omitir): ").strip()
            if entrada == "":
                return None
            val = int(entrada)
            if 1 <= val <= 5:
                return val
            print("  La valoración debe estar entre 1 y 5.")
        except ValueError:
            print("  Introduce un número válido.")

# ── Acciones ────────────────────────────────────────────────────────────────

def ver_todos(libros):
    mostrar_lista(libros, f"Todos los libros ({len(libros)})")

def agregar_libro(libros):
    titulo("Añadir nuevo libro")
    try:
        # ISBN con validación y normalización
        while True:
            entrada = input("  ISBN: ")
            normalizado = normalizar_isbn(entrada)

            if entrada.strip() == "":
                print("  El ISBN no puede estar vacío.")
                continue

            if not normalizado:
                print("  El ISBN no puede estar vacío.")
                continue

            if not normalizado.isdigit():
                print("  El ISBN debe contener solo números.")
                continue

            if isbn_duplicado(libros, normalizado):
                print("  Ya existe un libro con ese ISBN.")
                continue

            isbn = normalizado
            break
        # Intentar autocompletar desde Open Library
        print("  Buscando en Open Library...", end="", flush=True)
        datos = fetch_openlibrary(isbn)
        print(" ✓" if datos else " ✗")

        if datos:
            print("  Datos encontrados en Open Library (puedes editar):")
            t = input(f"  Título [{datos.get('titulo','')}]: ").strip() or datos.get('titulo','')
            a = input(f"  Autor [{datos.get('autor','')}]: ").strip() or datos.get('autor','')
            g = input(f"  Género [{datos.get('genero','')}]: ").strip() or datos.get('genero','')
            anio_str = input(f"  Año [{datos.get('anio','')}]: ").strip()
            pags_str = input(f"  Páginas [{datos.get('paginas','')}]: ").strip()

            anio = int(anio_str) if anio_str.isdigit() else datos.get('anio') or pedir_numero("  Año de publicación: ", 1, 2100)
            pags = int(pags_str) if pags_str.isdigit() else datos.get('paginas') or pedir_numero("  Número de páginas: ", 1, 99999)
        else:
            print("  No se encontraron datos automáticos. Introduce los datos manualmente.")
            t = input("  Título: ").strip()
            a = input("  Autor: ").strip()
            g = input("  Género: ").strip()
            anio = pedir_numero("  Año de publicación: ", 1, 2100)
            pags = pedir_numero("  Número de páginas: ", 1, 99999)
    except KeyboardInterrupt:
        print("\n  Cancelado.")
        return

    libro = Libro(titulo=t, autor=a, isbn=isbn, genero=g, anio=anio, paginas=pags)
    libros.append(libro)
    guardar_libros(libros)
    print(f'\n  ✓ "{t}" añadido correctamente.\n')

def marcar_leido(libros):
    pendientes = filtrar_pendientes(libros)
    if not pendientes:
        print("\n  No tienes libros pendientes.\n")
        return

    mostrar_lista(pendientes, "Libros pendientes")
    try:
        num = pedir_numero("  Número del libro leído: ", 1, len(pendientes))
        libro = pendientes[num - 1]
        val = pedir_valoracion()
        notas = input("  Notas (opcional): ").strip()
        libro.marcar_leido(val, notas)
        guardar_libros(libros)
        print(f'\n  ✓ "{libro.titulo}" marcado como leído.\n')
    except KeyboardInterrupt:
        print("\n  Cancelado.")

def buscar(libros):
    titulo("Buscar libros")
    print("  1. Por título")
    print("  2. Por autor")
    print("  3. Por género")
    print("  4. Por valoración mínima")
    opcion = input("\n  Opción: ").strip()

    if opcion == "1":
        texto = input("  Título: ").strip()
        mostrar_lista(buscar_por_titulo(libros, texto), f'Resultados para "{texto}"')
    elif opcion == "2":
        autor = input("  Autor: ").strip()
        mostrar_lista(buscar_por_autor(libros, autor), f'Libros de "{autor}"')
    elif opcion == "3":
        genero = input("  Género: ").strip()
        mostrar_lista(filtrar_por_genero(libros, genero), f'Género: {genero}')
    elif opcion == "4":
        minima = pedir_numero("  Valoración mínima (1-5): ", 1, 5)
        mostrar_lista(filtrar_por_valoracion(libros, minima), f"Valoración ≥ {minima}★")
    else:
        print("  Opción no válida.")

def ver_estadisticas(libros):
    stats = estadisticas(libros)
    if not stats:
        print("\n  La biblioteca está vacía.\n")
        return

    titulo("📊 Estadísticas de tu biblioteca")
    print(f"  Total de libros:     {stats['total']}")
    print(f"  Leídos:              {stats['leidos']}")
    print(f"  Pendientes:          {stats['pendientes']}")
    print(f"  Páginas leídas:      {stats['paginas_leidas']:,}")
    if stats["valoracion_media"]:
        print(f"  Valoración media:    {stats['valoracion_media']} ★")
    if stats["genero_favorito"]:
        print(f"  Género más leído:    {stats['genero_favorito']}")
    print("\n  Libros por género:")
    for genero, count in sorted(stats["generos"].items(), key=lambda x: -x[1]):
        barra = "█" * count
        print(f"    {genero:<20} {barra} ({count})")
    print()

def eliminar_libro(libros):
    mostrar_lista(libros, "Selecciona el libro a eliminar")
    if not libros:
        return
    try:
        num = pedir_numero("  Número del libro a eliminar: ", 1, len(libros))
        libro = libros[num - 1]
        confirmar = input(f'  ¿Seguro que quieres eliminar "{libro.titulo}"? (s/N): ').strip().lower()
        if confirmar == "s":
            libros.pop(num - 1)
            guardar_libros(libros)
            print(f'  ✓ "{libro.titulo}" eliminado.\n')
        else:
            print("  Cancelado.\n")
    except KeyboardInterrupt:
        print("\n  Cancelado.")

def isbn_duplicado(libros, isbn, libro_actual=None):
    for l in libros:
        if l.isbn == isbn and l is not libro_actual:
            return True
    return False

def normalizar_isbn(texto: str) -> str:
    # Quita espacios y guiones, deja solo dígitos si son válidos
    return texto.replace(" ", "").replace("-", "")

def fetch_openlibrary(isbn: str) -> dict | None:
    try:
        url = f"https://openlibrary.org/isbn/{isbn}.json"
        with urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read().decode())

        titulo = data.get("title")

        # Autor (puede requerir segunda llamada)
        autor = ""
        if data.get("authors"):
            key = data["authors"][0].get("key")
            if key:
                with urlopen(f"https://openlibrary.org{key}.json", timeout=5) as resp:
                    author_data = json.loads(resp.read().decode())
                    autor = author_data.get("name", "")

        genero = ""
        if data.get("subjects"):
            genero = data["subjects"][0]

        anio = None
        if data.get("publish_date"):
            # intentar extraer año
            for token in data["publish_date"].split():
                if token.isdigit() and len(token) == 4:
                    anio = int(token)
                    break

        paginas = data.get("number_of_pages")

        return {
            "titulo": titulo,
            "autor": autor,
            "genero": genero,
            "anio": anio,
            "paginas": paginas,
        }
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        return None

def editar_libro(libros):
    mostrar_lista(libros, "Selecciona el libro a editar")
    if not libros:
        return
    try:
        num = pedir_numero("  Número del libro a editar: ", 1, len(libros))
        libro = libros[num - 1]

        # Campos básicos
        nuevo = input(f"  Título actual: {libro.titulo}\n  Nuevo (Enter para mantener): ").strip()
        if nuevo:
            libro.titulo = nuevo

        nuevo = input(f"  Autor actual: {libro.autor}\n  Nuevo (Enter para mantener): ").strip()
        if nuevo:
            libro.autor = nuevo

        # ISBN con validación de duplicados
        while True:
            entrada = input(f"  ISBN actual: {libro.isbn}\n  Nuevo (Enter para mantener): ")
            if entrada.strip() == "":
                break

            normalizado = normalizar_isbn(entrada)

            if not normalizado:
                print("  El ISBN no puede estar vacío.")
                continue

            if not normalizado.isdigit():
                print("  El ISBN debe contener solo números.")
                continue

            if isbn_duplicado(libros, normalizado, libro):
                print("  Ya existe un libro con ese ISBN.")
                continue

            libro.isbn = normalizado
            break

        nuevo = input(f"  Género actual: {libro.genero}\n  Nuevo (Enter para mantener): ").strip()
        if nuevo:
            libro.genero = nuevo

        nuevo = input(f"  Año actual: {libro.anio}\n  Nuevo (Enter para mantener): ").strip()
        if nuevo:
            try:
                libro.anio = int(nuevo)
            except ValueError:
                print("  Año inválido, se mantiene el actual.")

        nuevo = input(f"  Páginas actuales: {libro.paginas}\n  Nuevo (Enter para mantener): ").strip()
        if nuevo:
            try:
                libro.paginas = int(nuevo)
            except ValueError:
                print("  Número inválido, se mantiene el actual.")

        # Estado leído
        estado = input("  ¿Leído? (s/n, Enter para mantener): ").strip().lower()
        if estado == "s" and not libro.leido:
            libro.marcar_leido()
        elif estado == "n" and libro.leido:
            libro.marcar_pendiente()

        # Valoración (solo si leído)
        if libro.leido:
            val = pedir_valoracion()
            libro.actualizar_valoracion(val)

        guardar_libros(libros)
        print(f'\n  ✓ "{libro.titulo}" actualizado.\n')

    except KeyboardInterrupt:
        print("\n  Cancelado.")

# ── Menú principal ───────────────────────────────────────────────────────────

MENU = """
  [bold cyan]1[/]. Ver todos los libros
  [bold cyan]2[/]. Ver libros leídos
  [bold cyan]3[/]. Ver libros pendientes
  [bold cyan]4[/]. Añadir libro
  [bold cyan]5[/]. Marcar libro como leído
  [bold cyan]6[/]. Buscar / filtrar
  [bold cyan]7[/]. Estadísticas
  [bold cyan]8[/]. Eliminar libro
  [bold cyan]9[/]. Editar libro
  [bold red]0[/]. Salir
"""

def main():
    libros = cargar_libros()
    titulo("📚 Mi Biblioteca Personal")
    print(f"  {len(libros)} libros cargados.\n")

    while True:
        console.print(MENU)
        opcion = input("  Elige una opción: ").strip()

        if opcion == "1":
            ver_todos(libros)
        elif opcion == "2":
            mostrar_lista(filtrar_leidos(libros), "Libros leídos")
        elif opcion == "3":
            mostrar_lista(filtrar_pendientes(libros), "Libros pendientes")
        elif opcion == "4":
            agregar_libro(libros)
        elif opcion == "5":
            marcar_leido(libros)
        elif opcion == "6":
            buscar(libros)
        elif opcion == "7":
            ver_estadisticas(libros)
        elif opcion == "8":
            eliminar_libro(libros)
        elif opcion == "9":
            editar_libro(libros)
        elif opcion == "0":
            print("\n  ¡Hasta pronto! Sigue leyendo 📖\n")
            break
        else:
            print("  Opción no válida.\n")


if __name__ == "__main__":
    main()
