# Planteamiento del proyecto — NeuroCheck

**Asignatura:** Compiladores · Periodo 2026-2  
**Estudiante:** Adrian Alexander Benavides Caguasango  
**Integrantes adicionales:** [Completar únicamente si corresponde]

## Título

**NeuroCheck: analizador léxico, sintáctico y semántico de configuraciones de redes neuronales**.

## Problema

Al definir una red neuronal densa, cada capa requiere una matriz de pesos cuyas dimensiones correspondan a la cantidad de entradas y neuronas. Un error como declarar `pesos=[5,2]` para una capa que recibe cuatro valores y produce dos salidas es detectable sin entrenar la red. Resulta útil comunicar esta incompatibilidad antes de intentar ejecutar cálculos.

## Objetivo general

Diseñar e implementar un analizador para un lenguaje específico de dominio (NeuroLang) que valide la estructura de redes neuronales densas y reporte errores de sintaxis y de dimensiones de matrices de pesos.

## Objetivos específicos

1. Definir una gramática pequeña para declaraciones de red, entrada y capas densas.
2. Aplicar análisis léxico y sintáctico mediante Lark y construir un AST.
3. Verificar las reglas semánticas de nombres, tamaño de entrada, número de neuronas y dimensiones de pesos.
4. Desarrollar una interfaz sencilla que muestre código, errores, tokens, árbol sintáctico y arquitectura validada.
5. Comprobar el comportamiento mediante casos válidos y ejemplos con errores.

## Alcance

Una red tiene un identificador, una declaración de `entrada N;` y al menos una instrucción `capa nombre: densa(unidades, pesos=[filas,columnas]);`. Se permiten comentarios iniciados con `#`. Se valida que `filas = entradas de la capa` y `columnas = número de neuronas`. El límite educativo elegido es 1 a 64 entradas o neuronas.

**Fuera del alcance:** entrenamiento, derivadas, gradcheck, actualización de pesos, validación de los valores numéricos de una matriz, PyTorch/TensorFlow y modelos de lenguaje.

## Aporte original

Las reglas de dimensiones entre capas con mensajes de diagnóstico y sugerencias de corrección forman el aporte central. Como elemento adicional se presenta una visualización de la arquitectura y el árbol sintáctico. Para un grupo de cuatro integrantes, conviene validar con el profesor si ambas extensiones satisfacen el requisito de la rúbrica.

## Enfoque de desarrollo

- **Semana 1:** problema, gramática y ejemplos.
- **Semana 2:** análisis léxico, parser y AST.
- **Semana 3:** validaciones semánticas y pruebas.
- **Semana 4:** interfaz, documentación y video.

## Fecha de entrega del curso

Según la guía del profesor: registro del proyecto el **24 de noviembre de 2026**; entrega del repositorio, el reporte y el video a más tardar el **2 de diciembre de 2026 a las 11:59 p. m.**
