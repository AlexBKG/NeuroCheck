# NeuroCheck — guía de sustentación

## Qué es el proyecto (explicación de 30 segundos)

«NeuroCheck es un analizador de un lenguaje que llamamos NeuroLang. El usuario declara la entrada de una red y sus capas densas. El programa reconoce tokens, verifica la gramática, construye un árbol y revisa que las dimensiones de los pesos coincidan con el número de neuronas. Si encuentra un problema, lo informa con una sugerencia. No entrenamos redes; aplicamos conceptos de compiladores a la configuración de una red neuronal».

## Recorrido por el código

**`neurocheck/grammar.lark`:** define las dos sentencias admitidas, el nombre de la red y la estructura de los delimitadores. Lark se encarga de generar lexer y parser a partir de esta gramática.

**`neurocheck/compiler.py`:** contiene `compile_source`, la función principal. Primero obtiene tokens con `parser.lex`. Después usa `parser.parse`, guarda el árbol y lo transforma en un AST. Luego recorre las instrucciones: registra la entrada, revisa los nombres de las capas y compara las dimensiones de los pesos.

**`neurocheck/cli.py`:** recibe un archivo `.neuro`, llama a `compile_source` y muestra los diagnósticos. Es evidencia de que la interfaz web no realiza la compilación.

**`app.py`:** implementa un servidor HTTP local y recibe el código mediante `/api/compile`. **`web/`:** contiene HTML, CSS y JavaScript para editar el texto, mostrar diagnósticos y presentar el SVG. No contiene reglas de aprendizaje.

**`tests/test_compiler.py`:** verifica escenarios correctos e incorrectos. Los ejemplos tienen archivos de entrada dedicados.

## La regla matemática que deben saber explicar

Si una capa anterior tiene **4 salidas** y la capa actual contiene **2 neuronas**, la matriz de pesos se declara como `[4,2]` según nuestra convención. Escribir `[5,2]` produce E201. La comprobación es una comparación de pares de enteros, no una derivada ni un proceso de aprendizaje.

## Demostración de cinco minutos (ensayo)

1. **0:00–0:35:** nombre, problema y objetivo.
2. **0:35–1:15:** ejemplo de red válida; explicar las dimensiones `[3,4]` y `[4,2]`.
3. **1:15–2:05:** mostrar tokens, árbol sintáctico, AST y tabla de símbolos.
4. **2:05–3:05:** cargar el ejemplo con `[5,2]`, señalar E201, corregirlo y volver a validar.
5. **3:05–3:45:** cargar error sintáctico y contrastarlo con el error semántico.
6. **3:45–4:25:** mostrar los archivos y ejecutar las 30 pruebas automatizadas con pytest.
7. **4:25–5:00:** aporte original, límites y cierre. Dejar un margen para edición del video.

## Preguntas probables del profesor

**¿Qué hace un lexer?** Divide la fuente en tokens con tipo, valor y ubicación. Nuestro lexer lo genera Lark a partir de la gramática.

**¿Qué valida el parser?** Que las instrucciones estén ordenadas según la gramática. Por ejemplo, espera `;` al final de una entrada.

**¿Qué es el AST?** Una representación organizada del programa: nombre de la red y sentencias normalizadas. No es lo mismo que el texto original ni que la visualización de neuronas.

**¿Qué significa análisis semántico?** Aplicar reglas que van más allá de la sintaxis, como exigir que la forma de `pesos` coincida con la entrada y salida de la capa.

**¿Por qué E201 es semántico y no sintáctico?** Porque `pesos=[5,2]` cumple la gramática; es inválido por su significado respecto a la capa anterior.

**¿Para qué sirve la tabla de símbolos?** Conserva la información relevante de las capas: identificador, entradas, neuronas y formas declarada/esperada de los pesos.

**¿Ustedes hicieron el parser desde cero?** No. Diseñamos la gramática y las reglas semánticas; Lark genera lexer y parser LALR. Es importante decirlo expresamente.

**¿Por qué usan HTML, CSS y JavaScript?** Para controlar directamente la maquetación y los temas claro/oscuro sin depender de estilos internos de otro framework. Python sigue realizando la compilación; la interfaz sólo presenta sus resultados.

**¿Dónde está la inteligencia artificial?** En el dominio de la herramienta: configuraciones de redes neuronales. NeuroCheck no contiene un modelo que aprenda ni un LLM.

**¿Valida realmente los pesos?** Valida **dimensiones declaradas**, no valores individuales ni comportamiento del entrenamiento. La distinción es central.

**¿Cuál es el aporte?** NeuroLang, diagnósticos por incompatibilidad dimensional y representación visual; la implementación se centra en técnicas del curso.

**¿Qué significa LALR?** Es una estrategia de análisis sintáctico ascendente; Lark genera el parser a partir de nuestra gramática.

## Ruta corta de estudio

Primero aprende la gramática y un ejemplo; luego recorre `compile_source` en orden; después estudia por qué el error de pesos es semántico; finalmente practica la demo y explica dos pruebas.
