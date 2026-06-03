from typing import List, Optional
from models.libro import Libro


def normalizar_genero(genero: str) -> str:
    return genero.strip().lower()


def buscar_por_titulo(libros: List[Libro], texto: str) -> List[Libro]:
    texto = texto.lower()
    return [l for l in libros if texto in l.titulo.lower()]


def buscar_por_autor(libros: List[Libro], autor: str) -> List[Libro]:
    autor = autor.lower()
    return [l for l in libros if autor in l.autor.lower()]


def filtrar_por_genero(libros: List[Libro], genero: str) -> List[Libro]:
    genero_norm = normalizar_genero(genero)
    return [l for l in libros if normalizar_genero(l.genero) == genero_norm]


def filtrar_leidos(libros: List[Libro]) -> List[Libro]:
    return [l for l in libros if l.leido]


def filtrar_pendientes(libros: List[Libro]) -> List[Libro]:
    return [l for l in libros if not l.leido]


def filtrar_por_valoracion(libros: List[Libro], minima: int) -> List[Libro]:
    return [l for l in libros if l.valoracion and l.valoracion >= minima]


def estadisticas(libros: List[Libro]) -> dict:
    if not libros:
        return {}

    leidos = [l for l in libros if l.leido]
    valorados = [l for l in leidos if l.valoracion]

    generos = {}
    for l in libros:
        key = normalizar_genero(l.genero)
        generos[key] = generos.get(key, 0) + 1

    return {
        "total": len(libros),
        "leidos": len(leidos),
        "pendientes": len(libros) - len(leidos),
        "paginas_leidas": sum(l.paginas for l in leidos),
        "valoracion_media": round(sum(l.valoracion for l in valorados) / len(valorados), 1) if valorados else None,
        "genero_favorito": max(generos, key=generos.get) if generos else None,
        "generos": generos,
    }
