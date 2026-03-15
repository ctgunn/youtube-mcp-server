"""Minimal HTTP entrypoint for hosted execution."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Mapping

from mcp_server.app import create_app
from mcp_server.protocol.envelope import error_response
from mcp_server.transport.http import JSON_CONTENT_TYPE, classify_hosted_request, hosted_status_code


@dataclass(frozen=True)
class HostedHTTPResult:
    status: int
    headers: dict[str, str]
    payload: dict


def _json_result(status: int, payload: dict) -> HostedHTTPResult:
    return HostedHTTPResult(
        status=status,
        headers={"Content-Type": JSON_CONTENT_TYPE},
        payload=payload,
    )


def execute_hosted_request(
    transport,
    *,
    method: str,
    path: str,
    headers: Mapping[str, str] | None = None,
    body: bytes | None = None,
) -> HostedHTTPResult:
    request_headers = {key.lower(): value for key, value in dict(headers or {}).items()}
    raw_body = body or b""
    classification = classify_hosted_request(
        method=method,
        path=path,
        content_type=request_headers.get("content-type"),
        body_present=bool(raw_body),
        body_valid=True,
    )

    if classification.outcome_class == "not_found":
        payload = transport.handle(path, {})
        return _json_result(hosted_status_code(classification, payload), payload)

    if classification.outcome_class == "method_not_allowed":
        payload = error_response(
            "METHOD_NOT_ALLOWED",
            "HTTP method is not allowed for this path.",
            details={"method": method.upper(), "path": path},
        )
        return _json_result(hosted_status_code(classification), payload)

    if path in {"/healthz", "/readyz"}:
        payload = transport.handle(path, {})
        return _json_result(hosted_status_code(classification, payload), payload)

    if classification.outcome_class == "unsupported_media_type":
        payload = error_response(
            "UNSUPPORTED_MEDIA_TYPE",
            "Content-Type must be application/json.",
            details={"contentType": request_headers.get("content-type")},
        )
        return _json_result(hosted_status_code(classification), payload)

    try:
        payload = json.loads(raw_body.decode("utf-8") or "{}") if raw_body else {}
    except json.JSONDecodeError:
        malformed = classify_hosted_request(
            method=method,
            path=path,
            content_type=request_headers.get("content-type"),
            body_present=bool(raw_body),
            body_valid=False,
        )
        return _json_result(hosted_status_code(malformed), error_response("INVALID_ARGUMENT", "payload must be valid JSON"))

    response = transport.handle(path, payload)
    return _json_result(hosted_status_code(classification, response), response)


def run_server() -> None:
    transport = create_app()
    port = int(os.environ.get("PORT", "8080"))

    class Handler(BaseHTTPRequestHandler):
        def _send_json(self, result: HostedHTTPResult) -> None:
            data = json.dumps(result.payload).encode("utf-8")
            self.send_response(result.status)
            for header, value in result.headers.items():
                self.send_header(header, value)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self) -> None:  # noqa: N802
            self._send_json(execute_hosted_request(transport, method="GET", path=self.path, headers=self.headers))

        def do_POST(self) -> None:  # noqa: N802
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length) if length else b""
            self._send_json(
                execute_hosted_request(
                    transport,
                    method="POST",
                    path=self.path,
                    headers=self.headers,
                    body=body,
                )
            )

        def do_PUT(self) -> None:  # noqa: N802
            self._send_json(execute_hosted_request(transport, method="PUT", path=self.path, headers=self.headers))

        def do_DELETE(self) -> None:  # noqa: N802
            self._send_json(execute_hosted_request(transport, method="DELETE", path=self.path, headers=self.headers))

        def log_message(self, format: str, *args) -> None:  # noqa: A003
            return

    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    run_server()
