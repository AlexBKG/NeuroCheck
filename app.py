"""Interfaz editorial de NeuroCheck: la lógica de compilación vive en neurocheck/."""
from __future__ import annotations

from html import escape
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from neurocheck.compiler import compile_source
from neurocheck.visualization import network_svg

ROOT = Path(__file__).resolve().parent
EXAMPLES = {
    "Red correcta": "red_correcta.neuro",
    "Error de pesos": "error_dimensiones.neuro",
    "Error de sintaxis": "error_sintaxis.neuro",
    "Error léxico": "error_lexico.neuro",
    "Nombre duplicado": "error_nombre_duplicado.neuro",
    "Entrada duplicada": "error_entrada_duplicada.neuro",
}

st.set_page_config(page_title="NeuroCheck · Compilador NeuroLang", page_icon="🧠", layout="wide")

# Estilos visuales exclusivamente: la verificación matemática no depende de CSS.
st.markdown("""
<style>
:root { --ink:#202C2A; --muted:#63716D; --peach:#EFAA94; --line:#E7E8E3; }
html, body, [data-testid="stAppViewContainer"], .stApp { background:#FAF9F6; color:var(--ink); }
[data-testid="stHeader"] { background:transparent; }
[data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"], #MainMenu, footer { display:none!important; }
[data-testid="stSidebar"] { background:#F3F2EE; border-right:1px solid #E6E6E0; }
[data-testid="stSidebar"] > div:first-child { padding-top:1.9rem; }
.block-container { max-width:1310px; padding-top:2rem; padding-bottom:4.5rem; }
.stMarkdown, .stText, p, label, input, textarea, button { font-family:Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont,"Segoe UI",Arial,sans-serif!important; }
.stMarkdown p { line-height:1.65; }
h1,h2,h3 { letter-spacing:-.035em!important; font-weight:700!important; color:var(--ink)!important; }
[data-testid="stSidebar"] .stMarkdown h2 {font-size:1.1rem!important;}
[data-testid="stMetric"] { padding:1rem 1.15rem; border:1px solid var(--line); border-radius:15px; background:#FFF; }
[data-testid="stMetricValue"] {font-size:1.85rem; color:#213633; letter-spacing:-.05em;}
[data-testid="stMetricLabel"] {color:#63716D;}
.stTextArea textarea {background:#fff!important; color:#263530!important; border:1px solid #DCDFD8!important; border-radius:13px!important; font-family:"Cascadia Code",Consolas,monospace!important; font-size:.92rem!important; line-height:1.58!important;}
.stTextArea textarea:focus {box-shadow:0 0 0 2px #F2BEAE!important; border-color:#E5A28D!important;}
.stSelectbox div[data-baseweb="select"] > div {background:#fff; border-color:#E1E4DD; border-radius:11px;}
.stButton>button, .stDownloadButton>button { border-radius:11px; border:1px solid #DADFD9; background:#fff; color:#2E403B; font-weight:600; padding:.55rem 1rem; }
.stButton>button:hover,.stDownloadButton>button:hover {border-color:#DD9886; color:#BD684F;}
[data-baseweb="tab-list"] {border-bottom:1px solid #E1E4DE; gap:1rem;}
button[data-baseweb="tab"] {color:#697672; font-size:.91rem;}
button[data-baseweb="tab"][aria-selected="true"] {color:#2C514B; border-bottom-color:#E6967D;}
[data-testid="stAlert"] {border-radius:13px;}
[data-testid="stDataFrame"], [data-testid="stTable"] {border-radius:13px; overflow:hidden;}
.nc-eyebrow {font-size:.72rem; font-weight:750; letter-spacing:.17em; color:#A76654; text-transform:uppercase;}
.nc-brand {display:flex;align-items:center;gap:12px;margin:.15rem 0 1.6rem;}
.nc-mark {display:flex;align-items:center;justify-content:center;height:40px;width:40px;border-radius:12px;color:#FFF;background:#293C36;font-weight:800;letter-spacing:-.05em;}
.nc-wordmark {font-size:1.23rem;font-weight:800;letter-spacing:-.045em;color:#263532;}
.nc-hero {padding:2.2rem 2.5rem 2.45rem;margin:0 0 1.85rem;border-radius:22px;border:1px solid #F0E9E2;background:linear-gradient(119deg,#FFEEE4 0%,#FFF8F2 47%,#EEF6F2 100%);position:relative;overflow:hidden;}
.nc-hero:after {content:"";position:absolute;right:-84px;top:-160px;height:345px;width:345px;border:1px solid rgba(221,159,138,.25);border-radius:50%;pointer-events:none;}
.nc-hero h1 {font-size:clamp(2.15rem,4vw,3.5rem)!important;line-height:1.10;margin:.75rem 0 .7rem;max-width:840px;letter-spacing:-.058em!important;}
.nc-hero p {margin:0;max-width:770px;color:#64726C;font-size:1rem;line-height:1.65;}
.nc-section {display:flex;align-items:center;gap:11px;margin:1rem 0 .85rem;}
.nc-index {color:#B06E5A;font-size:.75rem;font-weight:800;letter-spacing:.08em;}
.nc-section strong {font-size:1.12rem;color:#21332F;letter-spacing:-.025em;}
.nc-note {font-size:.87rem;color:#71807A;margin:.4rem 0 1rem;line-height:1.6;}
.nc-rule {height:1px;background:#E6E9E4;margin:1.1rem 0 1.2rem;}
.nc-status {padding:1.03rem 1.12rem;border-radius:13px;border:1px solid #CEE4D6;background:#EFF8F1;color:#325A47;font-size:.9rem;line-height:1.5;}
.nc-status.bad {border-color:#F0D4CA;background:#FFF3EF;color:#994F42;}
.nc-badge {display:inline-flex;align-items:center;gap:7px;border-radius:999px;border:1px solid #E4D9CF;background:#FFF9F5;padding:5px 11px;color:#9A6958;font-size:.72rem;font-weight:650;letter-spacing:.025em;}
.nc-mini {font-size:.78rem;color:#7B8780;line-height:1.55;}
.nc-diagnostic {border:1px solid #F1D9CF;border-left:3px solid #D98F78;background:#FFFBF8;border-radius:12px;margin:.72rem 0;padding:.85rem 1rem;color:#444F49;}
.nc-diagnostic strong {color:#925542;}
.nc-diagram-frame {margin-top:1.2rem;}
@media (max-width:770px){.block-container{padding:1.1rem 1rem 3rem;}.nc-hero{padding:1.55rem 1.3rem;}.nc-hero h1{font-size:2rem!important;}}
</style>""", unsafe_allow_html=True)


def header(number: str, text: str) -> None:
    st.markdown(
        f'<div class="nc-section"><span class="nc-index">{escape(number)}</span>'
        f'<strong>{escape(text)}</strong></div>', unsafe_allow_html=True,
    )


# La selección de un ejemplo es una acción explícita: modificar el editor no cambia el archivo.
with st.sidebar:
    st.markdown('<div class="nc-brand"><span class="nc-mark">N.</span><span class="nc-wordmark">NeuroCheck</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="nc-eyebrow">Área de trabajo</div>', unsafe_allow_html=True)
    choice = st.selectbox("Selecciona un ejemplo", options=list(EXAMPLES), index=0)
    if st.session_state.get("selected_example") != choice:
        st.session_state["source"] = (ROOT / "examples" / EXAMPLES[choice]).read_text(encoding="utf-8")
        st.session_state["selected_example"] = choice
    st.markdown('<div class="nc-rule"></div>', unsafe_allow_html=True)
    st.markdown('**Convención de pesos**')
    st.code('pesos=[entradas,neuronas]', language='text')
    st.markdown('<div class="nc-mini">Cambia el código del editor para experimentar. Los ejemplos originales no se modifican.</div>', unsafe_allow_html=True)
    st.markdown('<div class="nc-rule"></div>', unsafe_allow_html=True)
    st.markdown('<div class="nc-badge">NeuroLang · Proyecto académico</div>', unsafe_allow_html=True)

st.markdown('''<div class="nc-hero">
  <div class="nc-eyebrow">LENGUAJE · COMPILACIÓN · VALIDACIÓN</div>
  <h1>Redes neuronales, bajo análisis.</h1>
  <p>Escribe la estructura de una red en NeuroLang y descubre cómo un compilador detecta errores antes de ejecutar cálculos.</p>
</div>''', unsafe_allow_html=True)

editor_col, result_col = st.columns([1.12, .88], gap="large")
with editor_col:
    header("01 /", "Editor NeuroLang")
    source = st.text_area("Programa fuente", key="source", height=296, label_visibility="collapsed")
    st.download_button("Descargar código .neuro", data=source, file_name="mi_red.neuro", mime="text/plain")

result = compile_source(source)
with result_col:
    header("02 /", "Análisis del código")
    met1, met2, met3 = st.columns(3)
    met1.metric("Tokens", len(result.tokens))
    met2.metric("Errores", len(result.diagnostics))
    met3.metric("Capas", len(result.model.layers) if result.model else len([s for s in result.ast.get("statements", []) if s.get("kind") == "capa"]))
    if result.ok:
        st.markdown('<div class="nc-status"><strong>✓ Configuración válida.</strong><br>Gramática y dimensiones de las capas verificadas.</div>', unsafe_allow_html=True)
        st.markdown(f'<p class="nc-note">Red <strong>{escape(result.model.name)}</strong> · {len(result.model.layers)} capa(s) densa(s).</p>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="nc-status bad"><strong>Se detectaron errores.</strong><br>Revisa las ubicaciones y sugerencias siguientes.</div>', unsafe_allow_html=True)
        for diagnostic in result.diagnostics:
            loc = f'Línea {diagnostic.line}' if diagnostic.line else 'Configuración'
            body = f'<div class="nc-diagnostic"><strong>{escape(diagnostic.code)} · {escape(loc)}</strong><br>{escape(diagnostic.message)}'
            if diagnostic.suggestion:
                body += f'<br><span class="nc-mini">Sugerencia: {escape(diagnostic.suggestion)}</span>'
            st.markdown(body + '</div>', unsafe_allow_html=True)

st.markdown('<div class="nc-rule" style="margin-top:2.3rem"></div>', unsafe_allow_html=True)
phases, architecture = st.tabs(["Fases del compilador", "Arquitectura de la red"])
with phases:
    header("03 /", "De texto fuente a estructura validada")
    st.markdown('<p class="nc-note">Léxico → Sintaxis → Árbol sintáctico (AST) → Análisis semántico.</p>', unsafe_allow_html=True)
    t_tokens, t_ast, t_symbols = st.tabs(["Tokens", "Árbol y AST", "Tabla de símbolos"])
    with t_tokens:
        if result.tokens:
            st.dataframe(result.tokens, use_container_width=True, hide_index=True)
        else:
            st.info("No se reconocieron tokens; revisa la entrada.")
    with t_ast:
        st.code(result.parse_tree or "No hay árbol: corrige el error léxico o sintáctico.", language="text")
        if result.ast:
            st.json(result.ast)
    with t_symbols:
        if result.symbols:
            st.dataframe(result.symbols, use_container_width=True, hide_index=True)
        else:
            st.info("La tabla de símbolos aparece cuando se identifican capas.")
with architecture:
    header("04 /", "Visualización de la arquitectura")
    if result.ok:
        svg, note = network_svg(result.model)
        # Dimensión real del componente fijada; el SVG mantiene su relación de aspecto.
        # Antes se omitía width y el navegador lo agrandaba dentro de un iframe demasiado bajo.
        components.html(
            '<html><head><meta name="viewport" content="width=device-width, initial-scale=1" />'
            '<style>*{box-sizing:border-box}html,body{margin:0;padding:0;overflow:hidden;'
            'background:transparent}svg{display:block;width:100%;height:100%;max-height:405px}</style>'
            '</head><body><div style="width:100%;height:405px;overflow:hidden">'
            + svg + '</div></body></html>',
            height=407,
            scrolling=False,
        )
        st.markdown(f'<p class="nc-note">{escape(note)}</p>', unsafe_allow_html=True)
        st.dataframe(
            {
                "Capa": ["Entrada", *[l.name for l in result.model.layers]],
                "Neuronas": [result.model.input_dim, *[l.units for l in result.model.layers]],
            },
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("Para visualizar la arquitectura primero corrige los errores encontrados.")
