"""Minimal stdlib HTTP adapter for AgentService."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from os import environ
from urllib.parse import urlparse
import json

from deployment_runtime import AgentService


SERVICE = AgentService(environ.get("MODEL_ENDPOINT", "http://localhost:9000"))
SERVICE.mark_ready()


class Handler(BaseHTTPRequestHandler):
    def _write(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/healthz", "/readyz"):
            health = SERVICE.health()
            ok = health["live"] if path == "/healthz" else health["ready"]
            self._write(200 if ok else 503, health)
            return
        if path.startswith("/runs/"):
            try:
                self._write(200, SERVICE.get_run(path.rsplit("/", 1)[-1]))
            except KeyError as error:
                self._write(404, {"error": str(error)})
            return
        self._write(404, {"error": "not found"})

    def do_POST(self):
        if urlparse(self.path).path != "/runs":
            self._write(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            request = json.loads(self.rfile.read(length))
            self._write(202, SERVICE.create_run(request))
        except (ValueError, RuntimeError, json.JSONDecodeError) as error:
            self._write(400, {"error": str(error)})

    def log_message(self, format, *args):
        return


def main():
    port = int(environ.get("PORT", "8080"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
