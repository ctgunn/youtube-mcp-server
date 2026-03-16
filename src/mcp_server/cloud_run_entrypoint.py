"""Minimal HTTP entrypoint for hosted execution."""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Mapping
from urllib.parse import urlparse

from mcp_server.app import create_app
from mcp_server.protocol.envelope import error_response
from mcp_server.transport.http import JSON_CONTENT_TYPE, classify_hosted_request, hosted_status_code
from mcp_server.transport.streaming import (
    JSON_CONTENT_TYPE as STREAM_JSON_CONTENT_TYPE,
    MCP_PROTOCOL_VERSION_HEADER,
    MCP_SESSION_ID_HEADER,
    SSE_CONTENT_TYPE,
    SUPPORTED_MCP_PROTOCOL_VERSIONS,
    encode_sse,
    normalize_accept_header,
)


@dataclass(frozen=True)
class HostedHTTPResult:
    status: int
    headers: dict[str, str]
    payload: dict | None
    body: bytes


def _json_result(status: int, payload: dict, extra_headers: Mapping[str, str] | None = None) -> HostedHTTPResult:
    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": JSON_CONTENT_TYPE}
    if extra_headers:
        headers.update(extra_headers)
    return HostedHTTPResult(
        status=status,
        headers=headers,
        payload=payload,
        body=body,
    )


def _sse_result(status: int, body_text: str, extra_headers: Mapping[str, str] | None = None) -> HostedHTTPResult:
    headers = {
        "Content-Type": SSE_CONTENT_TYPE,
        "Cache-Control": "no-cache",
    }
    if extra_headers:
        headers.update(extra_headers)
    return HostedHTTPResult(
        status=status,
        headers=headers,
        payload=None,
        body=body_text.encode("utf-8"),
    )


def _empty_result(status: int, extra_headers: Mapping[str, str] | None = None) -> HostedHTTPResult:
    headers = dict(extra_headers or {})
    return HostedHTTPResult(
        status=status,
        headers=headers,
        payload=None,
        body=b"",
    )


def _normalize_headers(headers: Mapping[str, str] | None) -> dict[str, str]:
    return {key.lower(): value for key, value in dict(headers or {}).items()}


def _validate_origin(request_headers: Mapping[str, str]) -> bool:
    origin = request_headers.get("origin")
    if not origin:
        return True
    host = request_headers.get("host", "")
    origin_host = urlparse(origin).netloc
    if not origin_host:
        return False
    if origin_host == host:
        return True
    return origin_host.startswith("localhost") or origin_host.startswith("127.0.0.1")


def _protocol_version_or_default(request_headers: Mapping[str, str], payload: dict | None = None) -> str:
    header_version = request_headers.get(MCP_PROTOCOL_VERSION_HEADER.lower())
    if header_version:
        return header_version
    if isinstance(payload, dict) and payload.get("method") == "initialize":
        return SUPPORTED_MCP_PROTOCOL_VERSIONS[0]
    return SUPPORTED_MCP_PROTOCOL_VERSIONS[0]


def _require_accept(request_headers: Mapping[str, str], required: set[str]) -> bool:
    accept_types = normalize_accept_header(request_headers.get("accept"))
    return required.issubset(accept_types)


def execute_hosted_request(
    transport,
    *,
    method: str,
    path: str,
    headers: Mapping[str, str] | None = None,
    body: bytes | None = None,
) -> HostedHTTPResult:
    request_headers = _normalize_headers(headers)
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

    if path in {"/health", "/ready"}:
        payload = transport.handle(path, {})
        return _json_result(hosted_status_code(classification, payload), payload)

    if not _validate_origin(request_headers):
        return _json_result(403, error_response("FORBIDDEN", "Origin is not allowed."))

    if method.upper() == "GET":
        if not _require_accept(request_headers, {SSE_CONTENT_TYPE}):
            return _json_result(400, error_response("INVALID_ARGUMENT", "Accept must include text/event-stream."))
        session_id = request_headers.get(MCP_SESSION_ID_HEADER.lower())
        if not session_id:
            return _json_result(400, error_response("INVALID_ARGUMENT", "MCP-Session-Id is required."))
        try:
            protocol_version = _protocol_version_or_default(request_headers)
            if protocol_version not in SUPPORTED_MCP_PROTOCOL_VERSIONS:
                return _json_result(400, error_response("INVALID_ARGUMENT", "Unsupported MCP protocol version."))
            _ = transport.stream_manager.get_session(session_id)
        except KeyError:
            return _json_result(404, error_response("RESOURCE_NOT_FOUND", "Session not found.", details={"sessionId": session_id}))

        stream, events = transport.stream_manager.events_after(session_id, request_headers.get("last-event-id"))
        body_text = encode_sse(events)
        return _sse_result(
            200,
            body_text,
            extra_headers={
                MCP_SESSION_ID_HEADER: session_id,
                MCP_PROTOCOL_VERSION_HEADER: protocol_version,
                "X-Stream-Id": stream.stream_id,
            },
        )

    if not _require_accept(request_headers, {STREAM_JSON_CONTENT_TYPE, SSE_CONTENT_TYPE}):
        return _json_result(
            400,
            error_response("INVALID_ARGUMENT", "Accept must include application/json and text/event-stream."),
        )

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

    protocol_version = _protocol_version_or_default(request_headers, payload)
    if protocol_version not in SUPPORTED_MCP_PROTOCOL_VERSIONS:
        return _json_result(400, error_response("INVALID_ARGUMENT", "Unsupported MCP protocol version."))

    request_method = payload.get("method") if isinstance(payload, dict) else None
    session_id = request_headers.get(MCP_SESSION_ID_HEADER.lower())

    if request_method == "initialize":
        response = transport.handle(path, payload)
        session = transport.stream_manager.create_session(
            protocol_version=protocol_version,
            client_metadata=payload.get("params", {}).get("clientInfo") if isinstance(payload.get("params"), dict) else None,
        )
        return _json_result(
            200,
            response,
            extra_headers={
                MCP_SESSION_ID_HEADER: session.session_id,
                MCP_PROTOCOL_VERSION_HEADER: protocol_version,
            },
        )

    if not session_id:
        return _json_result(400, error_response("INVALID_ARGUMENT", "MCP-Session-Id is required."))
    try:
        transport.stream_manager.touch_session(session_id)
    except KeyError:
        return _json_result(404, error_response("RESOURCE_NOT_FOUND", "Session not found.", details={"sessionId": session_id}))

    if not payload.get("id"):
        return _empty_result(
            202,
            extra_headers={
                MCP_SESSION_ID_HEADER: session_id,
                MCP_PROTOCOL_VERSION_HEADER: protocol_version,
            },
        )

    response = transport.handle(path, payload)
    extra_headers = {
        MCP_SESSION_ID_HEADER: session_id,
        MCP_PROTOCOL_VERSION_HEADER: protocol_version,
    }
    if request_method == "tools/call":
        stream, events = transport.stream_manager.build_post_response_stream(session_id, str(payload.get("id")), response)
        extra_headers["X-Stream-Id"] = stream.stream_id
        return _sse_result(200, encode_sse(events), extra_headers=extra_headers)
    return _json_result(hosted_status_code(classification, response), response, extra_headers=extra_headers)


def run_server() -> None:
    transport = create_app(runtime_stdout=sys.stdout, runtime_stderr=sys.stderr)
    port = int(os.environ.get("PORT", "8080"))

    class Handler(BaseHTTPRequestHandler):
        def _send_result(self, result: HostedHTTPResult) -> None:
            data = result.body
            self.send_response(result.status)
            for header, value in result.headers.items():
                self.send_header(header, value)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            if data:
                self.wfile.write(data)

        def do_GET(self) -> None:  # noqa: N802
            self._send_result(execute_hosted_request(transport, method="GET", path=self.path, headers=self.headers))

        def do_POST(self) -> None:  # noqa: N802
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length) if length else b""
            self._send_result(
                execute_hosted_request(
                    transport,
                    method="POST",
                    path=self.path,
                    headers=self.headers,
                    body=body,
                )
            )

        def do_PUT(self) -> None:  # noqa: N802
            self._send_result(execute_hosted_request(transport, method="PUT", path=self.path, headers=self.headers))

        def do_DELETE(self) -> None:  # noqa: N802
            self._send_result(execute_hosted_request(transport, method="DELETE", path=self.path, headers=self.headers))

        def log_message(self, format: str, *args) -> None:  # noqa: A003
            return

    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    run_server()
