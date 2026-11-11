"""Servidor local de NeuroCheck.

La interfaz web está hecha con HTML, CSS y JavaScript. El análisis léxico,
sintáctico y semántico sigue siendo realizado exclusivamente en Python.

Ejecutar: python app.py
"""
from __future__ import annotations

import argparse
import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from neurocheck.compiler import compile_source
from neurocheck.visualization import network_svg

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
ASSETS = ROOT / "assets"
EXAMPLES = {
    "Red correcta": "red_correcta.neuro",
    "Error de pesos": "error_dimensiones.neuro",
    "Error de sintaxis": "error_sintaxis.neuro",
    "Error léxico": "error_lexico.neuro",
    "Nombre duplicado": "error_nombre_duplicado.neuro",
    "Entrada duplicada": "error_entrada_duplicada.neuro",
}
MAX_REQUEST_BYTES = 128 * 1024


class NeuroCheckHandler(BaseHTTPRequestHandler):
    server_version = "NeuroCheck/1.2"

    def _send_bytes(self, body: bytes, *, status: HTTPStatus = HTTPStatus.OK,
                    mime: str = "application/octet-stream") -> None:
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, value: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        self._send_bytes(json.dumps(value, ensure_ascii=False).encode("utf-8"),
                         status=status, mime="application/json; charset=utf-8")

    def _static(self, root: Path, rel: str) -> None:
        # Sólo se exponen archivos de web/ y assets/; no documentación ni código fuente.
        target = (root / rel).resolve()
        if not target.is_relative_to(root.resolve()) or not target.is_file():
            self._json({"error": "Recurso no encontrado."}, HTTPStatus.NOT_FOUND)
            return
        mime = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        if mime.startswith("text/") or mime in ("application/javascript", "image/svg+xml"):
            mime += "; charset=utf-8"
        self._send_bytes(target.read_bytes(), mime=mime)

    def do_GET(self) -> None:
        req = urlsplit(self.path)
        path = req.path
        if path in ("/", "/index.html"):
            return self._static(WEB, "index.html")
        if path in ("/styles.css", "/app.js"):
            return self._static(WEB, path.removeprefix("/"))
        if path.startswith("/assets/"):
            return self._static(ASSETS, path.removeprefix("/assets/"))
        if path == "/api/health":
            return self._json({"status": "ok", "version": "1.2.0"})
        if path == "/api/examples":
            return self._json({"examples": list(EXAMPLES)})
        if path == "/api/example":
            name = parse_qs(req.query).get("name", [""])[0]
            if name not in EXAMPLES:
                return self._json({"error": "Ejemplo desconocido."}, HTTPStatus.NOT_FOUND)
            source = (ROOT / "examples" / EXAMPLES[name]).read_text(encoding="utf-8")
            return self._json({"name": name, "source": source})
        return self._json({"error": "Recurso no encontrado."}, HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if urlsplit(self.path).path != "/api/compile":
            return self._json({"error": "Recurso no encontrado."}, HTTPStatus.NOT_FOUND)
        try:
            n = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return self._json({"error": "Content-Length inválido."}, HTTPStatus.BAD_REQUEST)
        if n <= 0 or n > MAX_REQUEST_BYTES:
            return self._json({"error": "El código excede el tamaño permitido o está vacío."},
                              HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
        try:
            payload = json.loads(self.rfile.read(n).decode("utf-8"))
            source = payload["source"]
            theme = payload.get("theme", "light")
            if not isinstance(source, str) or theme not in ("light", "dark"):
                raise ValueError("Datos no válidos")
            result = compile_source(source)
            response = result.as_dict()
            response["diagram_svg"], response["diagram_note"] = (
                network_svg(result.model, theme=theme) if result.ok else (None, None)
            )
            return self._json(response)
        except (ValueError, KeyError, TypeError, UnicodeError, json.JSONDecodeError):
            return self._json({"error": "La solicitud debe incluir source (texto) y theme (light/dark)."},
                              HTTPStatus.BAD_REQUEST)


def make_server(host: str = "127.0.0.1", port: int = 8501) -> ThreadingHTTPServer:
    """Construye el servidor; útil para pruebas sin arrancar el CLI."""
    return ThreadingHTTPServer((host, port), NeuroCheckHandler)


def main() -> None:
    cli = argparse.ArgumentParser(description="Servidor local de NeuroCheck")
    cli.add_argument("--host", default="127.0.0.1", help="Dirección local (por defecto 127.0.0.1)")
    cli.add_argument("--port", type=int, default=8501, help="Puerto HTTP (por defecto 8501)")
    args = cli.parse_args()
    try:
        with make_server(args.host, args.port) as httpd:
            print(f"NeuroCheck v1.2.0 disponible en http://{args.host}:{httpd.server_port}")
            print("Detén el servidor con Ctrl + C.")
            httpd.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        print("\nNeuroCheck detenido.")
    except OSError as exc:
        raise SystemExit(f"No se pudo iniciar el servidor: {exc}. Prueba con --port 8502.") from exc


if __name__ == "__main__":
    main()
