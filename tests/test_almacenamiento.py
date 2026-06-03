import json
from models.libro import Libro
import services.almacenamiento as storage


def test_guardar_y_cargar(tmp_path, monkeypatch):
    fake_file = tmp_path / "biblioteca.json"

    # Redirige el DATA_FILE al path temporal
    monkeypatch.setattr(storage, "DATA_FILE", str(fake_file))

    libros = [
        Libro("Dune", "Herbert", "1", "scifi", 1965, 400),
        Libro("1984", "Orwell", "2", "distopia", 1949, 300),
    ]

    storage.guardar_libros(libros)

    assert fake_file.exists()

    cargados = storage.cargar_libros()

    assert len(cargados) == 2
    assert cargados[0].titulo == "Dune"
