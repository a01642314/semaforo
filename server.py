"""
Servidor sencillo del semáforo ESP32 — solo librería estándar (sin pip).
- Sirve index.html / styles.css / app.js
- GET  /api/status -> estado actual + cuenta regresiva
- POST /api/update  <- ESP32 manda { "luz": "rojo|amarillo|verde", "restante": int? }

Uso:
    python3 server.py            # http://localhost:8000
    python3 server.py 8080       # otro puerto
"""
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

DURACIONES = {"rojo": 20, "verde": 15, "amarillo": 5}
PINES = {"rojo": 2, "amarillo": 4, "verde": 5}

# Última señal recibida del ESP32
estado = {"luz": "rojo", "restante": 20, "duracion": 20, "ts": 0.0}

TIMEOUT_CONEXION = 4.0  # si no hay POST en 4 s se considera desconectado


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # silencioso

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self._cors()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _static(self, path, ctype):
        try:
            with open(path, "rb") as f:
                body = f.read()
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except FileNotFoundError:
            self.send_error(404)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        p = urlparse(self.path).path
        if p in ("/", "/index.html"):
            return self._static("index.html", "text/html; charset=utf-8")
        if p == "/styles.css":
            return self._static("styles.css", "text/css")
        if p == "/app.js":
            return self._static("app.js", "application/javascript")
        if p == "/api/status":
            conectado = (time.time() - estado["ts"]) < TIMEOUT_CONEXION
            return self._json({
                "luz": estado["luz"],
                "restante": max(0, estado["restante"]),
                "duracion": estado["duracion"],
                "pines": PINES,
                "duraciones": DURACIONES,
                "conectado": conectado,
                "ultima_actualizacion": estado["ts"],
            })
        self.send_error(404)

    def do_POST(self):
        p = urlparse(self.path).path
        if p != "/api/update":
            return self.send_error(404)
        try:
            n = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return self._json({"error": "JSON inválido"}, 400)
        luz = str(data.get("luz", "")).lower()
        if luz not in DURACIONES:
            return self._json({"error": "luz debe ser rojo|amarillo|verde"}, 400)
        dur = int(data.get("duracion", DURACIONES[luz]))
        rest = data.get("restante", dur)
        try:
            rest = float(rest)
        except Exception:
            rest = dur
        estado.update({"luz": luz, "duracion": dur,
                       "restante": max(0, min(rest, dur)), "ts": time.time()})
        print(f"[ESP32] luz={luz} restante={estado['restante']:.0f}s pin={PINES[luz]}")
        return self._json({"ok": True, **estado})


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    srv = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"Semaforo server en http://localhost:{port}")
    print("  GET  /api/status   <- la pagina consulta cada 500 ms")
    print("  POST /api/update   <- el ESP32 manda {luz, restante}")
    srv.serve_forever()
