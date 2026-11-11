# Plan de pruebas y resultados — NeuroCheck

**Fecha de ejecución del motor:** 10 de noviembre de 2026.

Comando ejecutado en la raíz del proyecto:

```bash
python -m pytest -q
```

Resultado real en el entorno de desarrollo: **24 passed**.

## Casos cubiertos

| Grupo | Comprobación | Resultado esperado |
|---|---|---|
| Léxico | Tokenización de entrada válida | Tokens con línea y columna |
| Léxico | Símbolo `@` inesperado | E001 |
| Sintáctico | Falta de punto y coma | E002 |
| Sintáctico | Construcción de árbol y AST | Árbol y sentencias disponibles |
| Semántico | Red válida | Sin diagnósticos |
| Semántico | `pesos=[5,2]` donde se requiere `[4,2]` | E201 y sugerencia |
| Semántico | Nombre de capa repetido | E104 |
| Semántico | Entrada repetida | E103 |
| Semántico | Sin entrada | E101 |
| Semántico | Sin capa | E102 |
| Semántico | Tamaño de entrada cero | E105 |
| Semántico | Capa con cero neuronas | E106 |
| Estructura | Tabla de símbolos | Dimensiones registradas |
| Estructura | Tres capas correctas | Validación exitosa |
| Estructura | Error en segunda capa | E201 |
| Otros | Comentarios con `#` | Ignorados |
| Otros | Resultado serializable | Diccionario JSON-compatible |
| Otros | Error semántico | Sin modelo validado |

## Cómo repetir

```bash
python -m neurocheck.cli examples/red_correcta.neuro
python -m neurocheck.cli examples/error_dimensiones.neuro
python -m pytest -v
```

También se ejecutan 6 pruebas de `tests/test_visualization.py` para comprobar los límites del SVG, el conteo de neuronas y conexiones, los nombres largos, la reducción de redes extensas y que el visualizador no modifique el modelo.

La salida del ejemplo inválido finaliza con código 1 por diseño. La interfaz Streamlit requiere verificación visual adicional en el computador de los estudiantes. El conjunto de pruebas no abarca todas las posibles entradas al lenguaje.
