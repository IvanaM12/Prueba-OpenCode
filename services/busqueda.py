from typing import List, Optional
from models.libro import Libro


def normalizar_genero(genero: str) -> str:
    # Normaliza el género para comparaciones consistentes
    # - Elimina espacios al inicio/fin
    # - Convierte a minúsculas
    return genero.strip().lower()


def buscar_por_titulo(libros: List[Libro], texto: str) -> List[Libro]:
    # Devuelve libros cuyo título contiene el texto (búsqueda parcial)
    # La comparación es case-insensitive
    texto = texto.lower()
    return [l for l in libros if texto in l.titulo.lower()]


def buscar_por_autor(libros: List[Libro], autor: str) -> List[Libro]:
    # Devuelve libros cuyo autor contiene el texto indicado
    # Búsqueda parcial y sin distinguir mayúsculas/minúsculas
    autor = autor.lower()
    return [l for l in libros if autor in l.autor.lower()]


def filtrar_por_genero(libros: List[Libro], genero: str) -> List[Libro]:
    # Filtra libros por género exacto (tras normalizar formato)
    # Evita problemas por espacios o mayúsculas
    genero_norm = normalizar_genero(genero)
    return [l for l in libros if normalizar_genero(l.genero) == genero_norm]


def filtrar_leidos(libros: List[Libro]) -> List[Libro]:
    # Devuelve únicamente los libros marcados como leídos
    return [l for l in libros if l.leido]


def filtrar_pendientes(libros: List[Libro]) -> List[Libro]:
    # Devuelve los libros que aún no se han leído
    return [l for l in libros if not l.leido]


def filtrar_por_valoracion(libros: List[Libro], minima: int) -> List[Libro]:
    # Filtra libros con valoración mayor o igual a la mínima
    # Ignora libros sin valoración (None)
    return [l for l in libros if l.valoracion and l.valoracion >= minima]


def estadisticas(libros: List[Libro]) -> dict:
    # Calcula estadísticas agregadas de la colección de libros
    # Incluye totales, páginas leídas, media de valoración y géneros
    if not libros:
        return {}

    leidos = [l for l in libros if l.leido]
    # Libros que han sido leídos
    valorados = [l for l in leidos if l.valoracion]
    # Subconjunto de leídos que tienen valoración

    generos = {}
    for l in libros:
        # Cuenta cuántos libros hay por cada género normalizado
        key = normalizar_genero(l.genero)
        generos[key] = generos.get(key, 0) + 1

    return {
        "total": len(libros),
        "leidos": len(leidos),
        "pendientes": len(libros) - len(leidos),
        "paginas_leidas": sum(l.paginas for l in leidos),
        # Media de valoración (solo libros leídos y valorados)
        "valoracion_media": round(sum(l.valoracion for l in valorados) / len(valorados), 1) if valorados else None,
        # Género con mayor número de libros
        "genero_favorito": max(generos, key=generos.get) if generos else None,
        "generos": generos,
    }
