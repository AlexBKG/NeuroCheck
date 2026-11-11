"""Pruebas de regresión de la gráfica SVG y sus límites de visualización."""
from xml.etree import ElementTree as ET

from neurocheck.compiler import Layer, Model
from neurocheck.visualization import CANVAS_HEIGHT, CANVAS_WIDTH, network_svg


def example_model() -> Model:
    return Model("MiRed", 3, [Layer("oculta", 4, 3, 4, 1), Layer("salida", 2, 4, 2, 2)])


def test_svg_tiene_vista_completa_y_sin_recortes():
    svg, _ = network_svg(example_model())
    root = ET.fromstring(svg)
    assert root.attrib["viewBox"] == f"0 0 {CANVAS_WIDTH} {CANVAS_HEIGHT}"
    assert root.attrib["preserveAspectRatio"] == "xMidYMid meet"
    assert root.attrib["height"] == str(CANVAS_HEIGHT)


def test_grafica_dibuja_todas_las_neuronas_de_red_pequena():
    svg, _ = network_svg(example_model())
    root = ET.fromstring(svg)
    ns = {"s": "http://www.w3.org/2000/svg"}
    circles = root.findall(".//s:circle", ns)
    lines = root.findall(".//s:line", ns)
    assert len(circles) == 3 + 4 + 2
    assert len(lines) == (3 * 4) + (4 * 2) + 1  # 1 línea divisoria
    assert all(15 <= float(c.attrib["cy"]) <= CANVAS_HEIGHT - 15 for c in circles)


def test_agrupa_neuronas_grandes_sin_alterar_conteo_real():
    model = Model("Grande", 8, [Layer("oculta", 10, 8, 10, 1)])
    svg, note = network_svg(model)
    assert '+2 sin dibujar' in svg
    assert '+4 sin dibujar' in svg
    assert '8 neuronas' in svg and '10 neuronas' in svg
    assert 'tamaños indicados son los reales' in note


def test_nombres_largos_no_rompen_xml():
    model = Model("Grande", 2, [Layer('oculta_larga_abcdefgh', 2, 2, 2, 1)])
    svg, _ = network_svg(model)
    ET.fromstring(svg)
    assert 'oculta_larga_' in svg
    assert 'oculta_larga_abcdefgh' not in svg


def test_muchas_capas_se_resumen_sin_dibujar_conexiones_falsas():
    model = Model("Profunda", 1, [Layer(f'c{i}', 1, 1, 1, i) for i in range(10)])
    svg, note = network_svg(model)
    assert 'intermedias' in svg
    assert 'resumido' in note
    assert svg.count('<circle') == 6  # 3 capas al principio, 3 al final


def test_grafica_no_modifica_modelo():
    model = example_model()
    before = [(layer.name, layer.units) for layer in model.layers]
    network_svg(model)
    assert [(layer.name, layer.units) for layer in model.layers] == before
