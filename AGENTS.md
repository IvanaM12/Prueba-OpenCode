# AGENTS.md

## Entry point and execution
- Run app: `python main.py`
- No CLI args or env vars required.
- App is interactive; most logic is triggered via menu in `main.py`.

## Architecture (minimal mental model)
- `main.py`: orchestration + UI (terminal). All user flows live here.
- `models/libro.py`: core data model. Serialization via `to_dict` / `from_dict`.
- `services/almacenamiento.py`: persistence layer (JSON file).
- `services/busqueda.py`: pure functions for filtering/search/stats.

Data flow: `main -> services -> model -> JSON`.

## Persistence details (easy to break)
- Data file path is hardcoded relative to services:
  `services/../data/biblioteca.json`
- File is created automatically on first write.
- `Libro.from_dict(**data)` expects keys to match exactly the dataclass fields.
  Do not rename fields without migration logic.
- JSON uses `ensure_ascii=False` (UTF-8 expected).

## Import quirks
- `main.py` mutates `sys.path` to allow absolute imports from project root.
  Avoid refactoring imports without adjusting this or converting to a proper package.

## Behavior constraints
- `valoracion` is optional but, if present, must be `1-5`.
- `filtrar_por_valoracion` ignores books without rating (`None`).
- `estadisticas` returns `{}` for empty input (callers rely on falsy check).

## Testing / verification
- No test suite exists.
- Fast manual check:
  1. Run `python main.py`
  2. Add a book
  3. Restart app → verify persistence
  4. Mark as read → verify stats and filtering

## Safe change patterns
- Prefer adding logic in `services/` (pure functions) rather than bloating `main.py`.
- Keep `Libro` as the single source of truth for schema.
- Any schema change requires:
  - updating `to_dict` / `from_dict`
  - handling old JSON data (currently not implemented)

## Non-obvious pitfalls
- No validation on duplicate ISBNs.
- Case-insensitive search is implemented manually (`lower()`), keep consistent.
- `fecha_lectura` stored as ISO string, not `date` object.

## Extension hints (aligned with current design)
- New filters/search → add to `services/busqueda.py`
- New persistence format → isolate inside `almacenamiento.py`
- UI changes → confined to `main.py`
