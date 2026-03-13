"""Minimal HTTP entrypoint for hosted execution."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from mcp_server.app import create_app


def run_server() -> None:
    transport = create_app()
    port = int(os.environ.get("PORT", "8080"))

    class Handler(BaseHTTPRequestHandler):
        def _send_json(self, status: int, payload: dict) -> None:
            data = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self) -> None:  # noqa: N802
            if self.path not in {"/healthz", "/readyz"}:
                self._send_json(404, transport.handle(self.path, {}))
                return
            self._send_json(200, transport.handle(self.path, {}))

        def do_POST(self) -> None:  # noqa: N802
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length else b"{}"
            try:
                payload = json.loads(raw.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                self._send_json(400, {"success": False, "data": None, "meta": {"requestId": None}, "error": {"code": "INVALID_ARGUMENT", "message": "payload must be valid JSON", "details": None}})
                return
            response = transport.handle(self.path, payload)
            status = 200 if response.get("success", True) else 400
            self._send_json(status, response)

        def log_message(self, format: str, *args) -> None:  # noqa: A003
            return

    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    run_server()
