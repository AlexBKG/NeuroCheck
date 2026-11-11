# Verificación de NeuroCheck 1.2.0

## Pruebas automáticas

Ejecución del 11 de noviembre de 2026:

```text
python -m pytest -q
30 passed
```

El conjunto incluye 18 comprobaciones del compilador, seis pruebas de SVG y seis pruebas del servidor HTTP/interfaz.

## Revisión visual

Se cargaron directamente los archivos HTML, CSS y JavaScript de esta versión en Chromium, con las mismas estructuras de respuesta que devuelve `POST /api/compile`. Por separado se verificó que el servidor local y los endpoints respondan correctamente.

Se comprobó que:

- La barra lateral tenga la altura completa de una ventana de escritorio (940 px en la prueba).
- El tema claro y el oscuro utilicen paletas diferentes, incluidas las tablas y el editor.
- Los iconos de sol y luna cambien correctamente la apariencia.
- El diagrama SVG se renderice en los dos temas y no esté recortado.
- El programa con pesos incorrectos produzca E201 y sugiera `pesos=[4,2]`.
- En un ancho de 390 px, el selector de ejemplos siga siendo utilizable.
- No aparezcan errores JavaScript durante esas interacciones.

La revisión visual se hizo con respuestas equivalentes a la API porque el navegador automatizado del entorno no permite navegar directamente a `localhost`. **Antes de publicar esta versión se recomienda abrir la aplicación real en Windows con `python app.py`.**

## Qué no cambió

- Gramática de NeuroLang.
- Reglas semánticas y mensajes E001–E201.
- Interfaz de línea de comandos.

## Ejecución

```powershell
.\.venv\Scripts\python.exe app.py
```

Abrir `http://127.0.0.1:8501` y detener con `Ctrl + C`.
