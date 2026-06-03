from main import normalizar_isbn, isbn_duplicado
from models.libro import Libro


def test_normalizar_isbn_basic():
    assert normalizar_isbn("123 456") == "123456"
    assert normalizar_isbn("123-456") == "123456"
    assert normalizar_isbn(" 123 - 456 ") == "123456"


def test_normalizar_isbn_edge():
    assert normalizar_isbn("---") == ""
    assert normalizar_isbn("   ") == ""


def test_isbn_duplicado_detecta():
    l1 = Libro("A", "B", "123", "g", 2000, 100)
    l2 = Libro("C", "D", "456", "g", 2001, 200)
    libros = [l1, l2]

    assert isbn_duplicado(libros, "123") is True
    assert isbn_duplicado(libros, "789") is False


def test_isbn_duplicado_ignora_actual():
    l1 = Libro("A", "B", "123", "g", 2000, 100)
    libros = [l1]

    assert isbn_duplicado(libros, "123", l1) is False
