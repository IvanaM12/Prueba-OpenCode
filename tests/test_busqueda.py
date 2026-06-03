from models.libro import Libro
from services.busqueda import (
    buscar_por_titulo,
    buscar_por_autor,
    filtrar_por_genero,
    filtrar_leidos,
    filtrar_pendientes,
    filtrar_por_valoracion,
    estadisticas,
)


def sample_libros():
    l1 = Libro("Dune", "Herbert", "1", "scifi", 1965, 400, True, 5)
    l2 = Libro("1984", "Orwell", "2", "distopia", 1949, 300, False)
    l3 = Libro("Foundation", "Asimov", "3", "scifi", 1951, 250, True, 4)
    return [l1, l2, l3]


def test_buscar_por_titulo_case_insensitive():
    res = buscar_por_titulo(sample_libros(), "dune")
    assert len(res) == 1


def test_filtrar_genero_normalizado():
    res = filtrar_por_genero(sample_libros(), "SCIFI")
    assert len(res) == 2


def test_filtrar_leidos_pendientes():
    libros = sample_libros()
    assert len(filtrar_leidos(libros)) == 2
    assert len(filtrar_pendientes(libros)) == 1


def test_filtrar_por_valoracion():
    res = filtrar_por_valoracion(sample_libros(), 5)
    assert len(res) == 1


def test_estadisticas_basicas():
    stats = estadisticas(sample_libros())
    assert stats["total"] == 3
    assert stats["leidos"] == 2
    assert stats["pendientes"] == 1
    assert stats["paginas_leidas"] == 650
    assert stats["valoracion_media"] == 4.5


def test_estadisticas_vacia():
    assert estadisticas([]) == {}


def test_estadisticas_sin_valoraciones():
    l1 = Libro("A", "B", "1", "g", 2000, 100, True)
    l2 = Libro("C", "D", "2", "g", 2001, 200, True)
    stats = estadisticas([l1, l2])
    assert stats["valoracion_media"] is None
