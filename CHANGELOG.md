# Historial de cambios

## v1.2.0 — 11 de noviembre de 2026

### Interfaz

- Se sustituyó la interfaz Streamlit por HTML, CSS y JavaScript servidos desde Python estándar, manteniendo el mismo motor de compilación de NeuroLang.
- La barra lateral izquierda es fija y ocupa toda la altura de la ventana en escritorio; ya no se oculta ni necesita pestañas desplegables.
- Se revisaron la distribución, los márgenes, la jerarquía tipográfica y la separación entre bloques.
- Se incorporaron temas claro y oscuro con controles de sol y luna, selección guardada en el navegador y paletas completas para tablas, editor, botones y estados.
- Se mantuvo la fotografía de redes como fondo y se añadió una versión invertida para el tema oscuro.
- Se ajustó el efecto translúcido / liquid glass y el diagrama SVG para ambos temas.
- Se añadió un diseño adaptable a pantallas estrechas.

### Comportamiento y calidad

- La compilación se consulta mediante `POST /api/compile`, con ejemplos servidos por la misma aplicación.
- Se conserva `compile_source` y el conjunto de reglas del lenguaje.
- Se añadieron seis pruebas de API y de estructura del frontend: **30 pruebas aprobadas**.
- Se verificaron aspectos de presentación e interacciones en Chromium con una carga local de los archivos y respuestas de ejemplo; los endpoints se comprobaron de forma independiente.

## v1.1.0 — 10 de noviembre de 2026

- Se corrigió la geometría y el recorte del diagrama SVG.
- Se modernizó la primera interfaz Streamlit.
- Se separó `neurocheck/visualization.py` de la lógica de compilación.
- Se incorporaron pruebas de regresión visual estructural y automatización de CI.

## v1.0.0 — Versión inicial simplificada

- Se implementaron lexer, parser LALR, AST y verificación semántica de NeuroLang.
- Se añadieron diagnósticos, tabla de símbolos, interfaz y CLI.
- Se limitaron las redes a capas densas y comprobaciones de dimensiones.
