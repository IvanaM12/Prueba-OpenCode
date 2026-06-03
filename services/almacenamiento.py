import json
import os
from typing import List
from models.libro import Libro

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "biblioteca.json")


def cargar_libros() -> List[Libro]:
    """Carga los libros desde el archivo JSON."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            datos = json.load(f)
            return [Libro.from_dict(d) for d in datos]
    except (json.JSONDecodeError, KeyError):
        print("⚠ Error al leer la biblioteca. Se iniciará vacía.")
        return []


def guardar_libros(libros: List[Libro]) -> None:
    """Guarda la lista de libros en el archivo JSON."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([l.to_dict() for l in libros], f, ensure_ascii=False, indent=2)
