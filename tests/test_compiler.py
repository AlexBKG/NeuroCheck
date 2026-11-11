"""Pruebas de las fases principales del compilador NeuroLang."""
from pathlib import Path

from neurocheck.compiler import compile_source

EX = Path(__file__).resolve().parents[1] / "examples"


def codes(source):
    return {d.code for d in compile_source(source).diagnostics}


def test_red_valida():
    result = compile_source((EX / "red_correcta.neuro").read_text(encoding="utf-8"))
    assert result.ok
    assert result.model.name == "MiRed"
    assert result.model.input_dim == 3
    assert [layer.units for layer in result.model.layers] == [4, 2]


def test_lexer_reconoce_tokens():
    result = compile_source("red A { entrada 2; capa sal: densa(1, pesos=[2,1]); }")
    assert result.ok
    assert any(t["valor"] == "entrada" for t in result.tokens)
    assert all(t["linea"] >= 1 for t in result.tokens)


def test_arbol_y_ast():
    result = compile_source("red A { entrada 2; capa sal: densa(1, pesos=[2,1]); }")
    assert result.parse_tree.startswith("start")
    assert result.ast["name"] == "A"
    assert len(result.ast["statements"]) == 2


def test_tabla_de_simbolos():
    result = compile_source("red A { entrada 2; capa sal: densa(1, pesos=[2,1]); }")
    assert result.symbols[0]["entradas"] == 2
    assert result.symbols[0]["neuronas"] == 1


def test_error_lexico():
    assert "E001" in codes((EX / "error_lexico.neuro").read_text(encoding="utf-8"))


def test_error_sintaxis():
    assert "E002" in codes((EX / "error_sintaxis.neuro").read_text(encoding="utf-8"))


def test_dimensiones_incompatibles():
    result = compile_source((EX / "error_dimensiones.neuro").read_text(encoding="utf-8"))
    assert not result.ok
    assert "E201" in {d.code for d in result.diagnostics}
    assert "[4,2]" in result.diagnostics[0].suggestion


def test_nombre_duplicado():
    assert "E104" in codes((EX / "error_nombre_duplicado.neuro").read_text(encoding="utf-8"))


def test_entrada_duplicada():
    assert "E103" in codes((EX / "error_entrada_duplicada.neuro").read_text(encoding="utf-8"))


def test_falta_entrada():
    assert "E101" in codes("red A { capa sal: densa(2, pesos=[3,2]); }")


def test_falta_capa():
    assert "E102" in codes("red A { entrada 2; }")


def test_limite_entrada():
    assert "E105" in codes("red A { entrada 0; capa sal: densa(2, pesos=[0,2]); }")


def test_limite_neuronas():
    assert "E106" in codes("red A { entrada 2; capa sal: densa(0, pesos=[2,0]); }")


def test_comentarios_ignorados():
    result = compile_source("# Prueba\nred A { entrada 2; # nota\n capa sal: densa(1, pesos=[2,1]); }")
    assert result.ok


def test_serializacion_json():
    result = compile_source("red A { entrada 2; capa sal: densa(1, pesos=[2,1]); }")
    payload = result.as_dict()
    assert payload["ok"] and payload["model"]["name"] == "A"
    assert isinstance(payload["tokens"], list)


def test_error_no_tiene_modelo_ejecutable():
    result = compile_source("red A { entrada 2; capa sal: densa(1, pesos=[3,1]); }")
    assert not result.ok and result.model is None


def test_multiple_capas_correctas():
    source = "red A { entrada 2; capa a: densa(4, pesos=[2,4]); capa b: densa(3, pesos=[4,3]); capa c: densa(1, pesos=[3,1]); }"
    result = compile_source(source)
    assert result.ok and len(result.model.layers) == 3


def test_segunda_capa_incorrecta():
    source = "red A { entrada 2; capa a: densa(4, pesos=[2,4]); capa b: densa(1, pesos=[2,1]); }"
    assert "E201" in codes(source)
