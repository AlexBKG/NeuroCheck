"""Pruebas del servidor HTTP local y del contrato con la interfaz web."""
from __future__ import annotations

import json
import threading
from contextlib import contextmanager
from http.client import HTTPConnection
from pathlib import Path

from app import make_server


@contextmanager
def server_running():
    server = make_server("127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server.server_port
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def request(port: int, method: str, path: str, data=None):
    conn = HTTPConnection("127.0.0.1", port, timeout=5)
    headers = {}
    if data is not None:
        data = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    conn.request(method, path, data, headers)
    result = conn.getresponse()
    body = result.read()
    info = result.status, dict(result.getheaders()), body
    conn.close()
    return info


def test_server_hace_cargar_web_y_recursos():
    with server_running() as port:
        for path, content in [
            ("/", b'NeuroCheck'),
            ("/styles.css", b'html[data-theme="dark"]'),
            ("/app.js", b'compileNow'),
            ("/assets/network-background.jpg", b'\xff\xd8'),
            ("/assets/network-background-inverted.jpg", b'\xff\xd8'),
        ]:
            status, headers, body = request(port, "GET", path)
            assert status == 200
            assert content in body
            assert headers["X-Content-Type-Options"] == "nosniff"


def test_api_devuelve_ejemplo_y_red_valida():
    with server_running() as port:
        status, _, body = request(port, "GET", "/api/examples")
        assert status == 200
        assert "Red correcta" in json.loads(body)["examples"]
        status, _, body = request(port, "GET", "/api/example?name=Red%20correcta")
        example = json.loads(body)
        assert status == 200 and "entrada" in example["source"]
        status, _, body = request(port, "POST", "/api/compile", {"source": example["source"], "theme": "dark"})
        result = json.loads(body)
        assert status == 200
        assert result["ok"] is True
        assert len(result["model"]["layers"]) == 2
        assert "#17282E" in result["diagram_svg"]  # fondo SVG oscuro
        assert "Cada círculo" in result["diagram_note"]


def test_api_reporta_error_semantico_y_no_dibuja_red():
    with server_running() as port:
        _, _, body = request(port, "GET", "/api/example?name=Error%20de%20pesos")
        source = json.loads(body)["source"]
        status, _, body = request(port, "POST", "/api/compile", {"source": source, "theme": "light"})
        result = json.loads(body)
        assert status == 200
        assert not result["ok"]
        assert any(d["code"] == "E201" for d in result["diagnostics"])
        assert result["diagram_svg"] is None


def test_no_exponer_codigo_fuente_ni_archivos_arbitrarios():
    with server_running() as port:
        for path in ["/neurocheck/compiler.py", "/app.py", "/assets/../app.py", "/api/example?name=../../README.md"]:
            status, _, _ = request(port, "GET", path)
            assert status == 404


def test_api_rechaza_datos_invalidos():
    with server_running() as port:
        for payload in [{"source": 4}, {"source": "red x {}", "theme": "incorrecto"}, {}]:
            status, _, body = request(port, "POST", "/api/compile", payload)
            assert status == 400
            assert "error" in json.loads(body)


def test_interfaz_tiene_sidebar_siempre_visible_y_tema_por_iconos():
    root = Path(__file__).resolve().parents[1]
    html = (root / "web" / "index.html").read_text(encoding="utf-8")
    css = (root / "web" / "styles.css").read_text(encoding="utf-8")
    assert '<aside class="sidebar"' in html
    assert 'id="light-theme"' in html and 'id="dark-theme"' in html
    assert "sidebar-toggle" not in html
    assert "position: fixed; inset: 0 auto 0 0;" in css
    assert 'html[data-theme="dark"]' in css
    assert "--table-head" in css and "--code" in css
