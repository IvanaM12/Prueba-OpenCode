from rich.console import Console
from rich.table import Table

console = Console()


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


def mensaje_error(msg: str):
    console.print(f"  {msg}", style="red")


def mensaje_ok(msg: str):
    console.print(f"  {msg}", style="green")


def mensaje_info(msg: str):
    console.print(f"  {msg}", style="yellow")
