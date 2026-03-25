"""Hosted runtime entrypoint for local and Cloud Run execution."""

from __future__ import annotations

import json
import os
import sys
from contextlib import asynccontextmanager
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from time import perf_counter
from typing import Any, Mapping

from mcp_server.app import create_app
from mcp_server.config import load_hosted_runtime_settings
from mcp_server.health import RuntimeLifecycleState
from mcp_server.observability import RequestContext, generate_request_id
from mcp_server.protocol.envelope import error_response_for_category
from mcp_server.security import (
    browser_preflight_headers,
    browser_response_headers,
    evaluate_browser_preflight,
    evaluate_security_request,
)
from mcp_server.transport.http import JSON_CONTENT_TYPE, classify_hosted_request, hosted_security_status_code, hosted_status_code
from mcp_server.transport.streaming import (
    ExpiredSessionError,
    JSON_CONTENT_TYPE as STREAM_JSON_CONTENT_TYPE,
    MCP_PROTOCOL_VERSION_HEADER,
    MCP_SESSION_ID_HEADER,
    ReplayUnavailableError,
    SSE_CONTENT_TYPE,
    SUPPORTED_MCP_PROTOCOL_VERSIONS,
    InvalidSessionError,
    encode_sse,
    normalize_accept_header,
)

try:
    from fastapi import FastAPI, Request, Response
except ImportError:  # pragma: no cover - exercised when optional deps are absent
    FastAPI = None
    Request = Any
    Response = Any

try:
    import uvicorn
except ImportError:  # pragma: no cover - exercised when optional deps are absent
    uvicorn = None


@dataclass(frozen=True)
class HostedHTTPResult:
    status: int
    headers: dict[str, str]
    payload: dict | None
    body: bytes


class HostedASGIApplication:
    """ASGI wrapper around the hosted request executor."""

    def __init__(self, transport):
        self.transport = transport

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http":
            await send({"type": "http.response.start", "status": 500, "headers": []})
            await send({"type": "http.response.body", "body": b"Unsupported scope type."})
            return

        headers = {key.decode("latin-1"): value.decode("latin-1") for key, value in scope.get("headers", [])}
        body = b""
        more_body = True
        while more_body:
            message = await receive()
            body += message.get("body", b"")
            more_body = message.get("more_body", False)

        result = execute_hosted_request(
            self.transport,
            method=scope.get("method", "GET"),
            path=scope.get("path", "/"),
            headers=headers,
            body=body,
        )
        response_headers = [[key.encode("latin-1"), value.encode("latin-1")] for key, value in result.headers.items()]
        await send({"type": "http.response.start", "status": result.status, "headers": response_headers})
        await send({"type": "http.response.body", "body": result.body})


def _json_result(status: int, payload: dict, extra_headers: Mapping[str, str] | None = None) -> HostedHTTPResult:
    body = json.dumps(payload, sort_keys=True).encode("utf-8")
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


def _combine_headers(*mappings: Mapping[str, str] | None) -> dict[str, str]:
    headers: dict[str, str] = {}
    for mapping in mappings:
        if mapping:
            headers.update(mapping)
    return headers


def _normalize_headers(headers: Mapping[str, str] | None) -> dict[str, str]:
    return {key.lower(): value for key, value in dict(headers or {}).items()}


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


def _preflight_error_category(decision_category: str) -> str:
    return {
        "malformed_origin": "malformed_origin",
        "malformed_security_input": "malformed_security_input",
        "unsupported_browser_headers": "unsupported_browser_headers",
        "unsupported_browser_method": "unsupported_browser_method",
        "unsupported_browser_route": "unsupported_browser_route",
        "origin_denied": "origin_denied",
    }.get(decision_category, "forbidden")


def _request_error(category: str, message: str, *, request_id=None, details: Mapping[str, Any] | None = None) -> dict:
    return error_response_for_category(category, message, request_id=request_id, details=dict(details or {}))


def execute_hosted_request(
    transport,
    *,
    method: str,
    path: str,
    headers: Mapping[str, str] | None = None,
    body: bytes | None = None,
) -> HostedHTTPResult:
    started_at = perf_counter()
    request_headers = _normalize_headers(headers)
    raw_body = body or b""
    security_settings = transport.runtime_settings.security
    if method.upper() == "OPTIONS" and request_headers.get("origin"):
        request_id = generate_request_id()
        preflight = evaluate_browser_preflight(path=path, request_headers=request_headers, settings=security_settings)
        transport.observability.emit_security_decision(
            {
                "requestId": request_id,
                "path": path,
                "decision": "accepted" if preflight.decision_category == "approved" else "denied",
                "decisionCategory": preflight.decision_category,
                "failureLayer": "none" if preflight.decision_category == "approved" else "mcp_application",
                "clientType": "browser",
                "authPresent": False,
                "originPresent": True,
                "requestMethod": preflight.requested_method,
                "requestHeaders": list(preflight.requested_headers),
                "browserFlow": "preflight",
            }
        )
        if preflight.decision_category == "approved":
            return _empty_result(preflight.status_code, extra_headers=browser_preflight_headers(preflight, security_settings))
        return _json_result(
            preflight.status_code,
            _request_error(
                _preflight_error_category(preflight.decision_category),
                {
                    "origin_denied": "Origin is not allowed.",
                    "malformed_origin": "Security headers are malformed.",
                    "malformed_security_input": "Security headers are malformed.",
                    "unsupported_browser_route": "Browser access is not supported for this route.",
                    "unsupported_browser_method": "Browser access is not supported for this method.",
                    "unsupported_browser_headers": "Requested browser headers are not supported.",
                }.get(preflight.decision_category, "Browser preflight is not allowed."),
                request_id=request_id,
                details={"category": preflight.decision_category},
            ),
        )

    classification = classify_hosted_request(
        method=method,
        path=path,
        content_type=request_headers.get("content-type"),
        body_present=bool(raw_body),
        body_valid=True,
    )
    allowed_browser_headers = browser_response_headers(path=path, request_headers=request_headers, settings=security_settings)

    if classification.outcome_class == "not_found":
        payload = transport.handle(path, {})
        return _json_result(hosted_status_code(classification, payload), payload)

    if classification.outcome_class == "method_not_allowed":
        payload = _request_error(
            "method_not_allowed",
            "HTTP method is not allowed for this path.",
            details={"method": method.upper(), "path": path},
        )
        return _json_result(hosted_status_code(classification), payload)

    if path in {"/health", "/ready"}:
        payload = transport.handle(path, {})
        return _json_result(hosted_status_code(classification, payload), payload)

    request_id = generate_request_id()
    security_decision = evaluate_security_request(
        request_headers,
        security_settings,
        path=path,
        request_id=request_id,
        environment=transport.runtime_settings.environment,
    )
    transport.observability.emit_security_decision(
        {
            "requestId": security_decision.request_id,
            "path": security_decision.path,
            "decision": security_decision.decision,
            "decisionCategory": security_decision.decision_category,
            "failureLayer": "none" if security_decision.decision == "accepted" else "mcp_application",
            "clientType": security_decision.client_type,
            "authPresent": security_decision.auth_present,
            "originPresent": security_decision.origin_present,
        }
    )
    if not security_decision.tool_execution_allowed:
        transport.observability.record(
            RequestContext(request_id=security_decision.request_id, path=path),
            "error",
            (perf_counter() - started_at) * 1000.0,
        )
        message = {
            "unauthenticated": "Authentication is required.",
            "invalid_credential": "Credential is not valid for hosted MCP access.",
            "origin_denied": "Origin is not allowed.",
            "malformed_security_input": "Security headers are malformed.",
        }.get(security_decision.decision_category, "Hosted request is not allowed.")
        return _json_result(
            hosted_security_status_code(security_decision.decision_category),
            _request_error(
                security_decision.decision_category,
                message,
                request_id=security_decision.request_id,
                details={"category": security_decision.decision_category},
            ),
            extra_headers=allowed_browser_headers,
        )

    if method.upper() == "GET":
        if not _require_accept(request_headers, {SSE_CONTENT_TYPE}):
            return _json_result(
                400,
                _request_error("invalid_argument", "Accept must include text/event-stream."),
                extra_headers=allowed_browser_headers,
            )
        session_id = request_headers.get(MCP_SESSION_ID_HEADER.lower())
        if not session_id:
            return _json_result(
                400,
                _request_error("invalid_argument", "MCP-Session-Id is required."),
                extra_headers=allowed_browser_headers,
            )
        try:
            protocol_version = _protocol_version_or_default(request_headers)
            if protocol_version not in SUPPORTED_MCP_PROTOCOL_VERSIONS:
                return _json_result(
                    400,
                    _request_error("invalid_argument", "Unsupported MCP protocol version."),
                    extra_headers=allowed_browser_headers,
                )
            transport.stream_manager.touch_session(session_id)
            transport.observability.emit_session_decision(
                {"requestId": request_id, "path": path, "sessionId": session_id, "sessionOutcome": "continued"}
            )
        except InvalidSessionError:
            transport.observability.emit_session_decision(
                {
                    "requestId": request_id,
                    "path": path,
                    "sessionId": session_id,
                    "sessionOutcome": "invalid_session",
                    "reasonCode": "INVALID_SESSION",
                }
            )
            return _json_result(
                404,
                _request_error("session_not_found", "Session not found.", details={"sessionId": session_id}),
                extra_headers=allowed_browser_headers,
            )
        except ExpiredSessionError:
            transport.observability.emit_session_decision(
                {
                    "requestId": request_id,
                    "path": path,
                    "sessionId": session_id,
                    "sessionOutcome": "expired_session",
                    "reasonCode": "EXPIRED_SESSION",
                }
            )
            return _json_result(
                404,
                _request_error("expired_session", "Session expired.", details={"sessionId": session_id}),
                extra_headers=allowed_browser_headers,
            )

        try:
            stream, events = transport.stream_manager.events_after(session_id, request_headers.get("last-event-id"))
        except ReplayUnavailableError:
            transport.observability.emit_session_decision(
                {
                    "requestId": request_id,
                    "path": path,
                    "sessionId": session_id,
                    "sessionOutcome": "replay_unavailable",
                    "reasonCode": "REPLAY_UNAVAILABLE",
                }
            )
            return _json_result(
                409,
                _request_error(
                    "replay_unavailable",
                    "Replay history is no longer available for this session.",
                    details={"sessionId": session_id, "category": "replay_unavailable"},
                ),
                extra_headers=allowed_browser_headers,
            )
        body_text = encode_sse(events)
        return _sse_result(
            200,
            body_text,
            extra_headers=_combine_headers(
                allowed_browser_headers,
                {
                MCP_SESSION_ID_HEADER: session_id,
                MCP_PROTOCOL_VERSION_HEADER: protocol_version,
                "X-Stream-Id": stream.stream_id,
                },
            ),
        )

    if not _require_accept(request_headers, {STREAM_JSON_CONTENT_TYPE, SSE_CONTENT_TYPE}):
        return _json_result(
            400,
            _request_error("invalid_argument", "Accept must include application/json and text/event-stream."),
            extra_headers=allowed_browser_headers,
        )

    if classification.outcome_class == "unsupported_media_type":
        payload = _request_error(
            "unsupported_media_type",
            "Content-Type must be application/json.",
            details={"contentType": request_headers.get("content-type")},
        )
        return _json_result(hosted_status_code(classification), payload, extra_headers=allowed_browser_headers)

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
        return _json_result(
            hosted_status_code(malformed),
            _request_error("invalid_json", "payload must be valid JSON"),
            extra_headers=allowed_browser_headers,
        )

    protocol_version = _protocol_version_or_default(request_headers, payload)
    if protocol_version not in SUPPORTED_MCP_PROTOCOL_VERSIONS:
        return _json_result(
            400,
            _request_error("invalid_argument", "Unsupported MCP protocol version."),
            extra_headers=allowed_browser_headers,
        )

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
            extra_headers=_combine_headers(
                allowed_browser_headers,
                {
                MCP_SESSION_ID_HEADER: session.session_id,
                MCP_PROTOCOL_VERSION_HEADER: protocol_version,
                },
            ),
        )

    if not session_id:
        return _json_result(
            400,
            _request_error("invalid_argument", "MCP-Session-Id is required."),
            extra_headers=allowed_browser_headers,
        )
    try:
        transport.stream_manager.touch_session(session_id)
        transport.observability.emit_session_decision(
            {"requestId": request_id, "path": path, "sessionId": session_id, "sessionOutcome": "continued"}
        )
    except InvalidSessionError:
        transport.observability.emit_session_decision(
            {
                "requestId": request_id,
                "path": path,
                "sessionId": session_id,
                "sessionOutcome": "invalid_session",
                "reasonCode": "INVALID_SESSION",
            }
        )
        return _json_result(
            404,
            _request_error("session_not_found", "Session not found.", details={"sessionId": session_id}),
            extra_headers=allowed_browser_headers,
        )
    except ExpiredSessionError:
        transport.observability.emit_session_decision(
            {
                "requestId": request_id,
                "path": path,
                "sessionId": session_id,
                "sessionOutcome": "expired_session",
                "reasonCode": "EXPIRED_SESSION",
            }
        )
        return _json_result(
            404,
            _request_error("expired_session", "Session expired.", details={"sessionId": session_id}),
            extra_headers=allowed_browser_headers,
        )

    if not payload.get("id"):
        return _empty_result(
            202,
            extra_headers=_combine_headers(
                allowed_browser_headers,
                {
                MCP_SESSION_ID_HEADER: session_id,
                MCP_PROTOCOL_VERSION_HEADER: protocol_version,
                },
            ),
        )

    response = transport.handle(path, payload)
    extra_headers = _combine_headers(
        allowed_browser_headers,
        {
            MCP_SESSION_ID_HEADER: session_id,
            MCP_PROTOCOL_VERSION_HEADER: protocol_version,
        },
    )
    if request_method == "tools/call":
        stream, events = transport.stream_manager.build_post_response_stream(session_id, str(payload.get("id")), response)
        extra_headers["X-Stream-Id"] = stream.stream_id
        return _sse_result(200, encode_sse(events), extra_headers=extra_headers)
    return _json_result(hosted_status_code(classification, response), response, extra_headers=extra_headers)


def build_asgi_app(
    env: Mapping[str, str] | None = None,
    validate_startup: bool = True,
    runtime_stdout=None,
    runtime_stderr=None,
):
    transport = create_app(
        env=env,
        validate_startup=validate_startup,
        runtime_stdout=runtime_stdout,
        runtime_stderr=runtime_stderr,
    )
    transport.runtime_lifecycle = RuntimeLifecycleState()
    if not transport.startup_validation.is_valid:
        transport.runtime_lifecycle.mark_degraded(
            {
                "code": "CONFIG_VALIDATION_ERROR",
                "message": "Required configuration is invalid or incomplete.",
            }
        )

    def _start_runtime() -> None:
        durability = transport.stream_manager.durability_status(required=transport.runtime_settings.session.durability_required)
        if transport.startup_validation.is_valid and durability["available"]:
            transport.runtime_lifecycle.mark_ready()
            transport.observability.emit_runtime_event(
                "runtime.startup",
                "success",
                {"runtime": transport.runtime_settings.server_implementation},
            )
        else:
            reason = durability["reason"] if not durability["available"] else {
                "code": "CONFIG_VALIDATION_ERROR",
                "message": "Required configuration is invalid or incomplete.",
            }
            transport.runtime_lifecycle.mark_degraded(reason)
            transport.observability.emit_runtime_event("runtime.startup", "error")

    def _stop_runtime() -> None:
        transport.runtime_lifecycle.mark_stopping()
        transport.observability.emit_runtime_event("runtime.shutdown", "success")
        transport.runtime_lifecycle.mark_stopped()

    transport.start_runtime = _start_runtime
    transport.stop_runtime = _stop_runtime

    @asynccontextmanager
    async def _lifespan(_app):
        transport.start_runtime()
        try:
            yield
        finally:
            transport.stop_runtime()

    if FastAPI is not None:
        app = FastAPI(lifespan=_lifespan)

        @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
        async def hosted_route(request: Request, path: str) -> Response:
            body = await request.body()
            result = execute_hosted_request(
                transport,
                method=request.method,
                path="/" + path,
                headers=request.headers,
                body=body,
            )
            return Response(content=result.body, status_code=result.status, headers=result.headers)

        app.state.transport = transport
        return app

    return HostedASGIApplication(transport)


def run_server() -> None:
    runtime_settings = load_hosted_runtime_settings(os.environ)
    if uvicorn is not None:
        uvicorn.run(
            build_asgi_app(runtime_stdout=sys.stdout, runtime_stderr=sys.stderr),
            host=runtime_settings.host,
            port=runtime_settings.port,
            log_level=runtime_settings.log_level,
            reload=runtime_settings.reload_enabled,
        )
        return

    transport = create_app(runtime_stdout=sys.stdout, runtime_stderr=sys.stderr)
    port = runtime_settings.port

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

        def do_OPTIONS(self) -> None:  # noqa: N802
            self._send_result(execute_hosted_request(transport, method="OPTIONS", path=self.path, headers=self.headers))

        def log_message(self, format: str, *args) -> None:  # noqa: A003
            return

    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    run_server()


app = build_asgi_app(validate_startup=False)
