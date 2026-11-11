# Guion de video — NeuroCheck (máximo 5 minutos)

El documento del profesor establece un video de **máximo cinco minutos** centrado en la aplicación funcionando, con ejemplos, errores y fases relevantes. Este guion está pensado para una grabación de aproximadamente 4:30 a 4:50.

**00:00–00:30 · Introducción:** «NeuroCheck aplica análisis léxico, sintáctico y semántico a un pequeño lenguaje llamado NeuroLang, que sirve para describir capas densas de redes neuronales».

**00:30–01:15 · Programa válido:** mostrar `red_correcta.neuro`. Explicar que una entrada de 3 y una capa de 4 requieren pesos `[3,4]`; la siguiente capa de 2 requiere `[4,2]`.

**01:15–02:10 · Fases:** mostrar tokens y ubicación, árbol del parser, AST y tabla de símbolos. Nombrar los archivos `grammar.lark` y `compiler.py`.

**02:10–03:15 · Errores:** cargar `error_dimensiones.neuro`, señalar E201 y su sugerencia `[4,2]`; corregirlo desde el editor. Cargar `error_sintaxis.neuro` para diferenciar E002.

**03:15–03:55 · Arquitectura:** volver al ejemplo correcto y mostrar la visualización de capas. Aclarar que es un esquema estructural, no entrenamiento.

**03:55–04:30 · Pruebas:** ejecutar `python -m pytest -v` y mostrar el resultado. Presentar los módulos principales del repositorio.

**04:30–04:50 · Cierre:** sintetizar el aporte y sus limitaciones. Mostrar créditos reales de integrantes y recursos utilizados (Lark, Streamlit, documentación y uso de herramientas de IA).

**Recordatorio:** mostrar la extensión y sus efectos antes/después; no usar capturas simuladas como resultados obtenidos y verificar la duración final del video.
