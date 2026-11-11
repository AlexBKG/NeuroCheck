# Historial de cambios

Se registran versiones del **código**, sin inventar commits o atribuir fechas de trabajo no verificadas. El historial público de Git se generará al confirmar cada actualización en el repositorio.

## 1.1.0 — 10 de noviembre de 2026

### Corregido
- La arquitectura neuronal se muestra completa, sin el recorte vertical producido por la relación entre el SVG y el `iframe`.
- Los diagramas conservan una proporción fija y una escala adaptable al espacio disponible.
- Las etiquetas largas y las redes con muchas neuronas o capas cuentan con representación resumida.

### Mejorado
- Estilo minimalista con fondo claro, degradado suave, jerarquía tipográfica y márgenes más consistentes.
- Panel de resultados y visualización de diagnóstico más legibles.
- Separación de la generación de la gráfica en `neurocheck/visualization.py`.
- Se añadió integración continua para pruebas en GitHub Actions.

### Eliminado
- Texto redundante al final de la página.

### Pruebas
- 24 pruebas automatizadas aprobadas: 18 del compilador y 6 del visualizador.
- La interfaz Streamlit todavía requiere comprobación manual en navegador en el equipo del usuario.

## 1.0.0 — 10 de noviembre de 2026

- Lexer, parser LALR, AST y análisis semántico para el lenguaje NeuroLang.
- Verificación de dimensiones de matrices de pesos y sugerencias de corrección.
- Interfaz Streamlit, utilidad CLI, seis ejemplos y pruebas del compilador.
