# 📚 Mi Biblioteca Personal

Aplicación de terminal para gestionar tu colección de libros.

## Estructura del proyecto

```
biblioteca/
├── main.py                  # Punto de entrada y menú principal
├── models/
│   ├── __init__.py
│   └── libro.py             # Clase Libro con sus datos y métodos
├── services/
│   ├── __init__.py
│   ├── almacenamiento.py    # Leer y guardar datos en JSON
│   └── busqueda.py          # Búsquedas, filtros y estadísticas
└── data/
    └── biblioteca.json      # Base de datos (se crea automáticamente)
```

## Cómo ejecutarlo

```bash
python main.py
```

## Funcionalidades

- Ver todos los libros, leídos o pendientes
- Añadir nuevos libros manualmente
- Marcar libros como leídos con valoración y notas
- Buscar por título, autor, género o valoración mínima
- Ver estadísticas: páginas leídas, valoración media, géneros...
- Eliminar libros de la colección
- Los datos se guardan automáticamente en `data/biblioteca.json`

## Ideas para explorar con OpenCode 🤖

- Exportar la biblioteca a CSV o HTML
- Añadir un sistema de "lista de deseos" separado
- Importar libros desde la API de Open Library (openlibrary.org)
- Añadir soporte para series de libros
- Crear tests unitarios para los servicios
- Añadir colores con `colorama` o `rich` para mejorar la UI
- Detectar libros duplicados por ISBN
- Hacer una versión web con Flask
