"""Diagrama SVG independiente de Streamlit para redes NeuroLang válidas.

Solo representa capas y conexiones; no calcula valores ni entrena una red.
Se mantiene separado del compilador para facilitar pruebas y mantenimiento.
"""
from __future__ import annotations

from html import escape

from .compiler import Model

CANVAS_WIDTH = 1120
CANVAS_HEIGHT = 405
MAX_VISIBLE_NEURONS = 6
MAX_VISIBLE_COLUMNS = 7


def _short_label(name: str, limit: int = 15) -> str:
    return name if len(name) <= limit else name[: limit - 1] + "…"


def network_svg(model: Model, theme: str = "light") -> tuple[str, str]:
    """Devuelve (svg, leyenda) con tamaños y posiciones definidos en un viewBox.

    El SVG define dimensiones y viewBox explícitos; el contenedor web adapta
    su anchura manteniendo preserveAspectRatio para evitar recortes.
    Las neuronas dibujadas se limitan a 6.
    """
    # La geometría no depende del tema: sólo cambian los colores.
    if theme not in ("light", "dark"):
        raise ValueError("theme debe ser light o dark")
    palette = {
        "light": {
            "title": "#263B39", "muted": "#5D716C", "faint": "#82918E",
            "line": "#AFBFBB", "divider": "#DCE5E0", "border": "#DCE5E0",
            "surface0": "#FCFDFB", "surface1": "#F1F7F4",
            "input_fill": "#E9AA90", "input_stroke": "#BB755B",
            "mid_fill": "#94B8CA", "mid_stroke": "#5F8799",
            "output_fill": "#7FACA1", "output_stroke": "#4D8277",
        },
        "dark": {
            "title": "#E3F0EC", "muted": "#AEC5BD", "faint": "#849E97",
            "line": "#557A77", "divider": "#34524F", "border": "#375552",
            "surface0": "#17282E", "surface1": "#102027",
            "input_fill": "#CC896F", "input_stroke": "#E5B49C",
            "mid_fill": "#5C8AA2", "mid_stroke": "#A0C3D2",
            "output_fill": "#507F77", "output_stroke": "#A3D2C4",
        },
    }[theme]
    full_sizes = [model.input_dim, *(layer.units for layer in model.layers)]
    full_names = ["Entrada", *(layer.name for layer in model.layers)]
    column_count = len(full_sizes)
    if column_count <= MAX_VISIBLE_COLUMNS:
        indices: list[int | None] = list(range(column_count))
    else:
        indices = [0, 1, 2, None, column_count - 3, column_count - 2, column_count - 1]

    left_margin, right_margin = 116, CANVAS_WIDTH - 116
    step = (right_margin - left_margin) / max(len(indices) - 1, 1)
    x_positions = [left_margin + i * step for i in range(len(indices))]
    points: list[list[tuple[float, float]]] = []
    definitions: list[str] = []
    edges: list[str] = []
    nodes: list[str] = []
    footer: list[str] = []
    has_hidden_neurons = False

    for pos, index in enumerate(indices):
        x = x_positions[pos]
        if index is None:
            points.append([])
            definitions.append(
                f'<text x="{x:.1f}" y="77" text-anchor="middle" '
                f'fill="{palette['muted']}" font-size="15" font-weight="600">Capas</text>'
                f'<text x="{x:.1f}" y="101" text-anchor="middle" '
                f'fill="{palette['faint']}" font-size="13">intermedias</text>'
            )
            nodes.append(f'<text x="{x:.1f}" y="255" text-anchor="middle" font-size="36" fill="{palette['faint']}">···</text>')
            continue

        size = full_sizes[index]
        name = full_names[index]
        display = _short_label(name)
        definitions.extend([
            f'<text x="{x:.1f}" y="77" text-anchor="middle" '
            f'font-size="16" font-weight="650" fill="{palette['title']}">{escape(display)}</text>',
            f'<text x="{x:.1f}" y="101" text-anchor="middle" '
            f'font-size="13" fill="{palette['muted']}">{size} {"neurona" if size == 1 else "neuronas"}</text>',
        ])
        n_displayed = min(size, MAX_VISIBLE_NEURONS)
        has_hidden_neurons |= size > MAX_VISIBLE_NEURONS
        # Centro fijo y separación fija; la primera y última neurona nunca salen del lienzo.
        gap = 34
        center_y = 240
        ys = [center_y + (j - (n_displayed - 1) / 2) * gap for j in range(n_displayed)]
        visible = [(x, y) for y in ys]
        points.append(visible)
        fill = palette["input_fill"] if index == 0 else palette["output_fill"] if index == column_count - 1 else palette["mid_fill"]
        stroke = palette["input_stroke"] if index == 0 else palette["output_stroke"] if index == column_count - 1 else palette["mid_stroke"]
        for _, y in visible:
            nodes.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="14" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="1.5" />'
            )
        if size > MAX_VISIBLE_NEURONS:
            footer.append(
                f'<text x="{x:.1f}" y="369" text-anchor="middle" '
                f'fill="{palette['muted']}" font-size="12">+{size - MAX_VISIBLE_NEURONS} sin dibujar</text>'
            )

    # Conectar solo columnas consecutivas que realmente aparecen una junto a la otra.
    for pos, (index_a, index_b) in enumerate(zip(indices, indices[1:])):
        if index_a is None or index_b is None or index_b != index_a + 1:
            continue
        for x1, y1 in points[pos]:
            for x2, y2 in points[pos + 1]:
                edges.append(
                    f'<line x1="{x1 + 15:.1f}" y1="{y1:.1f}" '
                    f'x2="{x2 - 15:.1f}" y2="{y2:.1f}" '
                    f'stroke="{palette['line']}" stroke-opacity=".70" stroke-width="1.3" />'
                )

    defs = (f'<defs><linearGradient id="surface" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0%" stop-color="{palette["surface0"]}" />'
            f'<stop offset="100%" stop-color="{palette["surface1"]}" />'
            '</linearGradient></defs>')
    canvas = (
        f'<rect x="1" y="1" width="{CANVAS_WIDTH-2}" height="{CANVAS_HEIGHT-2}" '
        f'rx="19" fill="url(#surface)" stroke="{palette["border"]}" stroke-width="2" />'
    )
    divider = f'<line x1="55" y1="121" x2="1065" y2="121" stroke="{palette["divider"]}" />'
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_WIDTH}" height="{CANVAS_HEIGHT}" '
        f'viewBox="0 0 {CANVAS_WIDTH} {CANVAS_HEIGHT}" preserveAspectRatio="xMidYMid meet" '
        'role="img" aria-label="Diagrama de capas de la red neuronal">'
        + defs + canvas + divider + "".join(edges + definitions + nodes + footer) + '</svg>'
    )
    note = "Cada círculo representa una neurona y las líneas sus conexiones entre capas consecutivas."
    if has_hidden_neurons:
        note += " Por legibilidad, se dibujan hasta 6 neuronas por capa; los tamaños indicados son los reales."
    if None in indices:
        note += " Se han resumido algunas capas intermedias; no hay conexiones dibujadas a través del resumen."
    return svg, note
