import pytest
from models.libro import Libro


def test_from_dict_robusto_campos_basicos():
    data = {
        "titulo": "  Dune ",
        "autor": "Frank Herbert",
        "isbn": "123",
        "genero": "Sci-Fi ",
        "anio": "1965",
        "paginas": "412",
        "leido": True,
        "valoracion": 5,
        "fecha_lectura": "2024-01-01",
        "notas": "  clásico  ",
    }

    l = Libro.from_dict(data)

    assert l.titulo == "Dune"
    assert l.genero == "sci-fi"
    assert l.anio == 1965
    assert l.paginas == 412
    assert l.valoracion == 5
    assert l.notas == "clásico"


def test_from_dict_valoracion_invalida():
    data = {"titulo": "X", "autor": "Y", "isbn": "1", "genero": "g", "anio": 1, "paginas": 1, "valoracion": 10}
    l = Libro.from_dict(data)
    assert l.valoracion is None


def test_from_dict_datos_sucios():
    data = {
        "titulo": " Test ",
        "autor": " Autor ",
        "isbn": " 123 ",
        "genero": " Sci-Fi ",
        "anio": "abc",
        "paginas": None,
    }
    l = Libro.from_dict(data)

    assert l.titulo == "Test"
    assert l.autor == "Autor"
    assert l.genero == "sci-fi"
    assert l.anio == 0
    assert l.paginas == 0


def test_from_dict_vacio():
    l = Libro.from_dict({})
    assert l.titulo == ""
    assert l.autor == ""
    assert l.anio == 0


def test_marcar_leido_asigna_campos():
    l = Libro("t", "a", "i", "g", 2000, 100)
    l.marcar_leido(4, "bien")

    assert l.leido is True
    assert l.valoracion == 4
    assert l.notas == "bien"
    assert l.fecha_lectura is not None


def test_marcar_pendiente_limpia_campos():
    l = Libro("t", "a", "i", "g", 2000, 100, True, 5, "2024-01-01")
    l.marcar_pendiente()
    assert l.leido is False
    assert l.valoracion is None
    assert l.fecha_lectura is None


def test_actualizar_valoracion():
    l = Libro("t", "a", "i", "g", 2000, 100, True)
    l.actualizar_valoracion(4)
    assert l.valoracion == 4
    l.actualizar_valoracion(None)
    assert l.valoracion is None
