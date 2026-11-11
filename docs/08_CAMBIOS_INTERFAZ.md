# Revisión de interfaz — NeuroCheck 1.1.0

La revisión **no cambia las reglas del compilador**, la gramática ni el comportamiento de `compile_source`.

## Problema corregido

La versión anterior ponía un `<svg>` con un ancho relativo y sin un tamaño de presentación suficientemente controlado dentro de un `iframe` de altura fija. El navegador lo podía ampliar más que el espacio disponible, ocultando neuronas o conexiones.

Se extrajo el renderizador a `neurocheck/visualization.py`. Ahora el SVG tiene un `viewBox` estable, dimensiones explícitas y `preserveAspectRatio="xMidYMid meet"`; su contenedor conserva una altura adecuada para evitar recortes.

## Diseño

- Paleta clara (#FAF9F6 y #202C2A) con acento coral suave.
- Degradado discreto únicamente en el encabezado.
- Distribución editor/resultados y dos pestañas principales.
- Sin pie de página con el texto redundante de la versión anterior.
- El diseño evita dependencias externas de fuentes, imágenes y scripts.

## ¿Cómo probar visualmente?

1. Ejecutar `python -m streamlit run app.py`.
2. Elegir **Red correcta** y abrir **Arquitectura de la red**.
3. Confirmar que se ven **3 neuronas de entrada, 4 ocultas y 2 de salida**, sin cortes.
4. Elegir **Error de pesos**: deberá aparecer E201 y no mostrarse un diagrama validado.
5. Editar el código para corregir `pesos=[5,2]` por `pesos=[4,2]` y revisar que aparezca de nuevo el diagrama.
6. Reducir y ampliar el navegador; los elementos del SVG deben conservar su proporción.

Las pruebas automatizadas comprueban la estructura del SVG. La prueba final de percepción visual debe hacerse en el navegador, no sustituirse por el resultado de pytest.
