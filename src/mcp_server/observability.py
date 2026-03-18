"""Request observability helpers for logging and metrics."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import uuid
from typing import Any, TextIO


@dataclass
class RequestContext:
    request_id: str
    path: str
    method_name: str | None = None
    tool_name: str | None = None


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def generate_request_id() -> str:
    return f"req-{uuid.uuid4().hex}"


def build_request_context(path: str, payload: Any) -> RequestContext:
    request_id = None
    method_name = None
    tool_name = None

    if isinstance(payload, dict):
        raw_request_id = payload.get("id")
        if _is_non_empty_string(raw_request_id):
            request_id = raw_request_id
        raw_method = payload.get("method")
        if _is_non_empty_string(raw_method):
            method_name = raw_method

        params = payload.get("params")
        if isinstance(params, dict):
            raw_tool_name = params.get("name")
            if not _is_non_empty_string(raw_tool_name):
                raw_tool_name = params.get("toolName")
            if _is_non_empty_string(raw_tool_name):
                tool_name = raw_tool_name

    if request_id is None:
        request_id = generate_request_id()

    return RequestContext(
        request_id=request_id,
        path=path,
        method_name=method_name,
        tool_name=tool_name,
    )


def classify_endpoint(path: str) -> str:
    if path in {"/health", "/ready", "/mcp"}:
        return path
    return "not_found"


def runtime_event(event_name: str, status: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "severity": "INFO" if status == "success" else "ERROR",
        "event": event_name,
        "status": status,
    }
    if details:
        payload.update(details)
    return payload


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    index = round((len(sorted_values) - 1) * percentile)
    index = max(0, min(index, len(sorted_values) - 1))
    return sorted_values[index]


class InMemoryObservability:
    """Stores structured logs and metric aggregates for runtime introspection/tests."""

    def __init__(self, runtime_stdout: TextIO | None = None, runtime_stderr: TextIO | None = None):
        self._logs: list[dict[str, Any]] = []
        self._counts: dict[tuple[str, str, str | None], int] = {}
        self._latencies: dict[tuple[str, str | None], list[float]] = {}
        self._runtime_stdout = runtime_stdout
        self._runtime_stderr = runtime_stderr

    @property
    def logs(self) -> list[dict[str, Any]]:
        return list(self._logs)

    def count_for(self, endpoint: str, outcome: str, tool_name: str | None = None) -> int:
        return self._counts.get((endpoint, outcome, tool_name), 0)

    def snapshot(self) -> dict[str, Any]:
        endpoint_counts: dict[str, dict[str, int]] = {}
        for (endpoint, outcome, _tool_name), count in self._counts.items():
            bucket = endpoint_counts.setdefault(endpoint, {"success": 0, "error": 0})
            bucket[outcome] = bucket.get(outcome, 0) + count

        endpoint_latency: dict[str, dict[str, float]] = {}
        tool_latency: dict[str, dict[str, float]] = {}
        for (endpoint, tool_name), samples in self._latencies.items():
            payload = {
                "p50": _percentile(samples, 0.50),
                "p95": _percentile(samples, 0.95),
                "count": len(samples),
            }
            endpoint_latency[endpoint] = payload
            if tool_name:
                tool_latency[tool_name] = payload

        return {
            "counts": endpoint_counts,
            "latency": {
                "byEndpoint": endpoint_latency,
                "byTool": tool_latency,
            },
        }

    def record(self, context: RequestContext, outcome: str, latency_ms: float):
        endpoint = classify_endpoint(context.path)
        tool_name = context.tool_name if context.method_name == "tools/call" else None
        self._counts[(endpoint, outcome, tool_name)] = self._counts.get((endpoint, outcome, tool_name), 0) + 1

        latency_key = (endpoint, tool_name)
        self._latencies.setdefault(latency_key, []).append(max(float(latency_ms), 0.0))

        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "severity": "INFO" if outcome == "success" else "ERROR",
            "requestId": context.request_id,
            "path": context.path,
            "status": outcome,
            "latencyMs": round(max(float(latency_ms), 0.0), 3),
        }
        if context.method_name:
            event["methodName"] = context.method_name
        if tool_name:
            event["toolName"] = tool_name
        self._logs.append(event)
        self._emit_runtime_event(event)

    def emit_security_decision(self, decision: dict[str, Any]) -> None:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "severity": "INFO" if decision.get("decision") == "accepted" else "ERROR",
            "event": "security.decision",
            "requestId": decision.get("requestId"),
            "path": decision.get("path"),
            "status": "success" if decision.get("decision") == "accepted" else "error",
            "decision": decision.get("decision"),
            "decisionCategory": decision.get("decisionCategory"),
            "clientType": decision.get("clientType"),
            "authPresent": bool(decision.get("authPresent")),
            "originPresent": bool(decision.get("originPresent")),
        }
        self._logs.append(event)
        self._emit_runtime_event(event)

    def _emit_runtime_event(self, event: dict[str, Any]) -> None:
        stream = self._runtime_stderr if event["status"] == "error" else self._runtime_stdout
        if stream is None:
            return
        stream.write(json.dumps(event, sort_keys=True) + "\n")
        if hasattr(stream, "flush"):
            stream.flush()

    def emit_runtime_event(self, event_name: str, status: str, details: dict[str, Any] | None = None) -> None:
        self._emit_runtime_event(runtime_event(event_name, status, details))
