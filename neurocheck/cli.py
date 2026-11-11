"""Interfaz de consola para NeuroCheck. Ejecutar: python -m neurocheck.cli ..."""
import argparse
import json
from pathlib import Path

from .compiler import compile_source


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="NeuroCheck: análisis de redes NeuroLang")
    parser.add_argument("archivo", type=Path, help="Archivo .neuro que se va a analizar")
    parser.add_argument("--tokens", action="store_true", help="Mostrar tokens")
    parser.add_argument("--arbol", action="store_true", help="Mostrar árbol sintáctico")
    parser.add_argument("--json", action="store_true", help="Mostrar resultado completo como JSON")
    args = parser.parse_args(argv)
    try:
        source = args.archivo.read_text(encoding="utf-8")
    except OSError as exc:
        parser.error(str(exc))
    result = compile_source(source)
    if args.json:
        print(json.dumps(result.as_dict(), indent=2, ensure_ascii=False))
    else:
        print(f"NeuroCheck · {args.archivo}")
        print(f"Tokens: {len(result.tokens)} · Capas: {len(result.symbols)}")
        if args.tokens:
            for token in result.tokens:
                print(f"  [{token['tipo']}] {token['valor']!r} ({token['linea']}:{token['columna']})")
        if args.arbol:
            print("\nÁrbol sintáctico:\n" + (result.parse_tree or "No disponible"))
        if result.ok:
            print(f"ANÁLISIS CORRECTO: red '{result.model.name}' · dimensiones compatibles")
        else:
            for diagnostic in result.diagnostics:
                print(f"[{diagnostic.code}] línea {diagnostic.line}, columna {diagnostic.column}: {diagnostic.message}")
                if diagnostic.suggestion:
                    print(f"  Sugerencia: {diagnostic.suggestion}")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
