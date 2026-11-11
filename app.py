"""Interfaz visual del compilador NeuroCheck. No contiene lógica semántica."""
from __future__ import annotations

from html import escape
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from neurocheck.compiler import Model, compile_source

ROOT = Path(__file__).resolve().parent
EXAMPLES = {
    "Red correcta": "red_correcta.neuro",
    "Error de pesos": "error_dimensiones.neuro",
    "Error de sintaxis": "error_sintaxis.neuro",
    "Error léxico": "error_lexico.neuro",
    "Nombre duplicado": "error_nombre_duplicado.neuro",
    "Entrada duplicada": "error_entrada_duplicada.neuro",
}

st.set_page_config(page_title="NeuroCheck | Compiladores", page_icon="🧠", layout="wide")
st.markdown("""<style>
.block-container {max-width: 1240px; padding-top: 1.4rem}
h1 {letter-spacing: -.035em}
.caption {font-size: .88rem; color: #8397b4}
</style>""", unsafe_allow_html=True)


def network_svg(model: Model) -> tuple[str, int]:
    """SVG estático: dibuja hasta 6 neuronas de cada capa, sin dependencias gráficas."""
    sizes = [model.input_dim] + [layer.units for layer in model.layers]
    labels = ["Entrada"] + [layer.name for layer in model.layers]
    width = max(560, 190 * len(sizes))
    height = 310
    xs = [90 + i * (width - 180) / max(1, len(sizes) - 1) for i in range(len(sizes))]
    points = []
    for size, x in zip(sizes, xs):
        n = min(size, 6)
        points.append([(x, 95 + j * 27 + (6 - n) * 13.5) for j in range(n)])
    lines = []
    for left, right in zip(points[:-1], points[1:]):
        for x1, y1 in left:
            for x2, y2 in right:
                lines.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#5688A9" stroke-opacity=".30" stroke-width="1"/>')
    circles = []
    for i, (size, x, col) in enumerate(zip(sizes, xs, points)):
        circles.append(f'<text x="{x:.1f}" y="41" text-anchor="middle" fill="#C8D5E9" font-size="15" font-weight="600">{escape(labels[i])}</text>')
        circles.append(f'<text x="{x:.1f}" y="62" text-anchor="middle" fill="#8FA5C0" font-size="12">{size} neuronas</text>')
        for px, py in col:
            fill = "#48B7A0" if i == 0 else "#6699DD"
            circles.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="11" fill="{fill}" stroke="#D5E9FF" stroke-width="1.5"/>')
        if size > 6:
            circles.append(f'<text x="{x:.1f}" y="280" text-anchor="middle" fill="#B2C0D5" font-size="12">+ {size-6} no mostradas</text>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="Arquitectura de la red">' + "".join(lines + circles) + '</svg>'
    html = f'<div style="background:#142036;border:1px solid #30445f;border-radius:14px;padding:10px">{svg}</div>'
    return html, height + 20


st.title("🧠 NeuroCheck")
st.caption("Compilador educativo de NeuroLang · lexer · parser · validación semántica de pesos")
st.info("El programa analiza **la estructura de las capas y las dimensiones de sus pesos**. No entrena redes neuronales ni ejecuta inteligencia artificial.")

with st.sidebar:
    st.header("Ejemplos NeuroLang")
    selection = st.selectbox("Seleccionar un ejemplo", list(EXAMPLES))
    if st.session_state.get("example_name") != selection:
        st.session_state["source"] = (ROOT / "examples" / EXAMPLES[selection]).read_text(encoding="utf-8")
        st.session_state["example_name"] = selection
    st.caption("Puedes modificar el código libremente. El ejemplo original no cambia.")
    st.markdown("**Convención:** `pesos=[entradas,neuronas]`")

left, right = st.columns([1.12, 0.88], gap="large")
with left:
    st.subheader("01 · Editor")
    source = st.text_area("Código NeuroLang", key="source", height=305)
    st.download_button("Descargar .neuro", data=source, file_name="mi_red.neuro", mime="text/plain")

result = compile_source(source)
with right:
    st.subheader("02 · Resultado")
    a, b = st.columns(2)
    a.metric("Tokens", len(result.tokens))
    b.metric("Errores", len(result.diagnostics))
    if result.ok:
        st.success("Análisis correcto: estructura y dimensiones compatibles.")
        st.write(f"Red: **{result.model.name}** · Capas: **{len(result.model.layers)}**")
    else:
        st.error("Hay errores que deben corregirse.")
        for diagnostic in result.diagnostics:
            st.markdown(f"**{diagnostic.code}** · Línea {diagnostic.line} · {diagnostic.message}")
            if diagnostic.suggestion:
                st.caption("Sugerencia: " + diagnostic.suggestion)

phases, architecture = st.tabs(["🔎 Fases del compilador", "🕸️ Arquitectura de la red"])
with phases:
    st.markdown("**Lexer:** tokens. **Parser:** aplica la gramática LALR. **AST:** representa las instrucciones. **Semántica:** valida nombres y dimensiones.")
    tab1, tab2, tab3 = st.tabs(["Tokens", "Árbol sintáctico y AST", "Tabla de símbolos"])
    with tab1:
        st.dataframe(result.tokens, use_container_width=True, hide_index=True)
    with tab2:
        st.code(result.parse_tree or "No se pudo construir por un error léxico o sintáctico.", language="text")
        if result.ast:
            st.json(result.ast)
    with tab3:
        st.dataframe(result.symbols, use_container_width=True, hide_index=True)
with architecture:
    if result.ok:
        picture, size = network_svg(result.model)
        components.html(picture, height=size, scrolling=False)
        st.caption("La vista representa neuronas y conexiones. Si una capa tiene más de seis neuronas, se muestra una muestra visual.")
        st.table({"Capa": ["Entrada"] + [x.name for x in result.model.layers],
                  "Neuronas": [result.model.input_dim] + [x.units for x in result.model.layers]})
    else:
        st.info("Corrige los errores para mostrar la arquitectura validada.")

st.divider()
st.caption("NeuroCheck · Proyecto académico de Compiladores 2026-2 · Sin entrenamiento, gradcheck ni servicios externos.")
