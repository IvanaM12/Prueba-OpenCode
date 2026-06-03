from dataclasses import dataclass, field
from datetime import date
from typing import Optional
from datetime import datetime


@dataclass
class Libro:
    titulo: str
    autor: str
    isbn: str
    genero: str
    anio: int
    paginas: int
    leido: bool = False
    valoracion: Optional[int] = None  # 1-5
    fecha_lectura: Optional[str] = None
    notas: str = ""

    def __post_init__(self):
        # Normalize strings
        self.titulo = (self.titulo or "").strip()
        self.autor = (self.autor or "").strip()

        # Titulo obligatorio
        if not self.titulo:
            raise ValueError("El título no puede estar vacío.")

        # Autor: default si vacío
        if not self.autor:
            self.autor = "Desconocido"

        # Paginas > 0
        try:
            self.paginas = int(self.paginas)
        except (TypeError, ValueError):
            raise ValueError("El número de páginas debe ser un entero válido.")
        if self.paginas <= 0:
            raise ValueError("El número de páginas debe ser mayor que 0.")

        # Año <= año actual
        current_year = datetime.now().year
        try:
            self.anio = int(self.anio)
        except (TypeError, ValueError):
            raise ValueError("El año debe ser un número válido.")
        if self.anio > current_year:
            raise ValueError(f"El año no puede ser mayor que {current_year}.")

    def marcar_leido(self, valoracion: Optional[int] = None, notas: str = ""):
        self.leido = True
        self.fecha_lectura = date.today().isoformat()
        if valoracion and 1 <= valoracion <= 5:
            self.valoracion = valoracion
        if notas:
            self.notas = notas

    # Nuevos métodos para edición más granular
    def marcar_pendiente(self):
        self.leido = False
        self.fecha_lectura = None
        self.valoracion = None

    def actualizar_valoracion(self, valoracion: Optional[int]):
        if valoracion is None:
            self.valoracion = None
        elif isinstance(valoracion, int) and 1 <= valoracion <= 5:
            self.valoracion = valoracion

    def to_dict(self) -> dict:
        return {
            "titulo": self.titulo,
            "autor": self.autor,
            "isbn": self.isbn,
            "genero": self.genero,
            "anio": self.anio,
            "paginas": self.paginas,
            "leido": self.leido,
            "valoracion": self.valoracion,
            "fecha_lectura": self.fecha_lectura,
            "notas": self.notas,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Libro":
        def safe_int(value, default=0):
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        valoracion = data.get("valoracion")
        if not isinstance(valoracion, int) or not (1 <= valoracion <= 5):
            valoracion = None

        return cls(
            titulo=str(data.get("titulo", "")).strip(),
            autor=str(data.get("autor", "")).strip(),
            isbn=str(data.get("isbn", "")).strip(),
            genero=str(data.get("genero", "")).strip().lower(),
            anio=safe_int(data.get("anio")),
            paginas=safe_int(data.get("paginas")),
            leido=bool(data.get("leido", False)),
            valoracion=valoracion,
            fecha_lectura=data.get("fecha_lectura"),
            notas=str(data.get("notas", "")).strip(),
        )

    def __str__(self) -> str:
        filled = self.valoracion or 0
        empty = 5 - filled
        estrellas = ("[yellow]" + "★" * filled + "[/]") if filled else ""
        if empty:
            estrellas += f"[dim]{'☆' * empty}[/]"
        estado = f"Leído {estrellas}" if self.leido else "[cyan]Pendiente[/]"
        texto = f'"{self.titulo}" — {self.autor} ({self.anio}) [{estado}]'
        # Color whole line for unread books
        if not self.leido:
            return f"[cyan]{texto}[/]"
        return texto
