# Revisión visual — NeuroCheck 1.2.0

La actualización mantiene **sin cambios las reglas del compilador**. El frontend se reemplazó para eliminar inconsistencias de estilos y garantizar un comportamiento más predecible.

## Cambios

- Barra lateral izquierda de altura completa en escritorio, siempre visible, con contenidos organizados desde la parte superior.
- Selector de apariencia con iconos de sol y luna; el modo elegido se conserva en el navegador.
- Paletas separadas para fondo, editor, botones, tarjetas, estados, tablas y diagrama SVG; el modo oscuro no utiliza paneles blancos.
- Imagen de fondo proporcionada por el usuario, con variante invertida para el modo oscuro.
- Efecto translúcido tipo glass en las tarjetas, con desenfoque, borde sutil y sombras moderadas.
- Espaciado consistente entre encabezado, editor, diagnóstico y resultados.
- Vista adaptable: en pantallas estrechas la barra lateral se convierte en encabezado compacto con selector de ejemplos.
- Servidor local HTTP estándar (`app.py`) y cliente HTML/CSS/JS en `web/`.

## Comprobación

1. Ejecutar `python app.py` y abrir `http://127.0.0.1:8501`.
2. Revisar que el panel izquierdo ocupe toda la altura en escritorio.
3. Cambiar entre sol y luna: no deben quedar controles blancos en modo oscuro.
4. Verificar la tabla de tokens y la arquitectura en ambos temas.
5. Seleccionar *Error de pesos*: debe aparecer E201 y la sugerencia `[4,2]`.
6. Ejecutar `python -m pytest -q`: deben aprobarse **30 pruebas**.

## Alcance

El frontend sólo consume los resultados de `compile_source`, no sustituye sus fases ni implementa nuevas reglas de validación.
