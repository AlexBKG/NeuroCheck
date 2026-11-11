"""Compilador educativo para NeuroLang.

Fases: lexing -> parsing LALR -> AST -> análisis semántico.
No entrena redes neuronales ni calcula gradientes: solo valida estructuras.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

from lark import Lark, Token, Transformer, Tree, UnexpectedCharacters, UnexpectedInput


@dataclass(frozen=True)
class Diagnostic:
    code: str
    message: str
    line: int = 0
    column: int = 0
    suggestion: str = ""


@dataclass(frozen=True)
class Layer:
    name: str
    units: int
    weight_rows: int
    weight_cols: int
    line: int


@dataclass(frozen=True)
class Model:
    name: str
    input_dim: int
    layers: list[Layer]


@dataclass
class CompilationResult:
    tokens: list[dict[str, Any]] = field(default_factory=list)
    parse_tree: str = ""
    ast: dict[str, Any] = field(default_factory=dict)
    symbols: list[dict[str, Any]] = field(default_factory=list)
    diagnostics: list[Diagnostic] = field(default_factory=list)
    model: Model | None = None

    @property
    def ok(self) -> bool:
        return self.model is not None and not self.diagnostics

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "tokens": self.tokens,
            "parse_tree": self.parse_tree,
            "ast": self.ast,
            "symbols": self.symbols,
            "diagnostics": [asdict(d) for d in self.diagnostics],
            "model": asdict(self.model) if self.model is not None else None,
        }


@lru_cache(maxsize=1)
def _parser() -> Lark:
    grammar = Path(__file__).with_name("grammar.lark").read_text(encoding="utf-8")
    return Lark(grammar, parser="lalr", propagate_positions=True)


class _ToAst(Transformer):
    """Transforma un árbol de Lark en sentencias sencillas para la semántica."""
    def input_statement(self, children):
        number = children[0]
        return {"kind": "entrada", "size": int(number), "line": number.line}

    def layer_statement(self, children):
        name, count, rows, cols = children
        return {"kind": "capa", "name": str(name), "units": int(count),
                "rows": int(rows), "cols": int(cols), "line": name.line}

    def start(self, children):
        return {"kind": "red", "name": str(children[0]), "statements": children[1:]}


def _diagnostic_for_exception(exc: UnexpectedInput, source: str) -> Diagnostic:
    line = getattr(exc, "line", 0) or 0
    column = getattr(exc, "column", 0) or 0
    if isinstance(exc, UnexpectedCharacters):
        return Diagnostic("E001", "Carácter no permitido en NeuroLang.", line, column,
                          "Revise el carácter señalado y los símbolos admitidos por la gramática.")
    return Diagnostic("E002", "La estructura no cumple la gramática de NeuroLang.", line, column,
                      "Revise llaves, paréntesis, comas, el punto y coma y las palabras reservadas.")


def compile_source(source: str) -> CompilationResult:
    """Analiza una cadena y devuelve datos para CLI, pruebas e interfaz."""
    result = CompilationResult()
    parser = _parser()

    # Análisis léxico: conserva los tokens incluso cuando falla la sintaxis.
    try:
        result.tokens = [
            {"tipo": token.type, "valor": str(token), "linea": token.line, "columna": token.column}
            for token in parser.lex(source)
        ]
    except UnexpectedInput as exc:
        result.diagnostics.append(_diagnostic_for_exception(exc, source))
        return result

    # Análisis sintáctico y construcción de una representación intermedia (AST).
    try:
        tree = parser.parse(source)
    except UnexpectedInput as exc:
        result.diagnostics.append(_diagnostic_for_exception(exc, source))
        return result
    result.parse_tree = tree.pretty()
    result.ast = _ToAst().transform(tree)

    # Análisis semántico: reglas no expresables solo con la gramática.
    statements = result.ast["statements"]
    inputs = [item for item in statements if item["kind"] == "entrada"]
    layers_raw = [item for item in statements if item["kind"] == "capa"]

    def error(code: str, message: str, line: int = 0, suggestion: str = "") -> None:
        result.diagnostics.append(Diagnostic(code, message, line, 0, suggestion))

    if not inputs:
        error("E101", "La red debe declarar una entrada.", suggestion="Añada: entrada 2;")
    if len(inputs) > 1:
        error("E103", "La entrada está declarada más de una vez.", inputs[1]["line"],
              "Deje una única instrucción entrada.")
    if not layers_raw:
        error("E102", "La red debe contener al menos una capa densa.",
              suggestion="Añada: capa salida: densa(1, pesos=[2,1]);")

    input_dim = inputs[0]["size"] if inputs else 0
    if inputs and not 1 <= input_dim <= 64:
        error("E105", "El tamaño de entrada debe estar entre 1 y 64.", inputs[0]["line"])

    names: set[str] = set()
    layers: list[Layer] = []
    previous = input_dim
    for item in layers_raw:
        layer = Layer(item["name"], item["units"], item["rows"], item["cols"], item["line"])
        layers.append(layer)
        if layer.name in names:
            error("E104", f"Nombre de capa repetido: '{layer.name}'.", layer.line,
                  "Use un identificador diferente para cada capa.")
        names.add(layer.name)
        if not 1 <= layer.units <= 64:
            error("E106", f"La capa '{layer.name}' debe tener entre 1 y 64 neuronas.", layer.line)
        if (layer.weight_rows, layer.weight_cols) != (previous, layer.units) and inputs:
            error("E201", f"Pesos incompatibles en '{layer.name}': declarados "
                  f"[{layer.weight_rows},{layer.weight_cols}], esperados [{previous},{layer.units}].",
                  layer.line, f"Cambie a pesos=[{previous},{layer.units}].")
        result.symbols.append({
            "capa": layer.name, "entradas": previous if inputs else "?",
            "neuronas": layer.units, "pesos declarados": f"[{layer.weight_rows},{layer.weight_cols}]",
            "pesos esperados": f"[{previous},{layer.units}]" if inputs else "?",
        })
        previous = layer.units

    if not result.diagnostics:
        result.model = Model(result.ast["name"], input_dim, layers)
    return result
