#!/usr/bin/env python3
"""Hosted verification CLI for the foundation Cloud Run deployment.

The verifier preserves the hosted streamable transport while validating
protocol-native MCP request and response bodies, including numeric MCP error
codes for covered failure paths.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from urllib import error, request

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mcp_server.deploy import HostedRevisionRecord, run_hosted_verification, write_verification_evidence  # noqa: E402


def _http_request(base_url: str, path: str, payload: object) -> dict:
    if not hasattr(_http_request, "_session_id"):
        _http_request._session_id = None  # type: ignore[attr-defined]
    url = f"{base_url.rstrip('/')}{path}"
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    auth_token = getattr(_http_request, "_auth_token", None)
    origin = getattr(_http_request, "_origin", None)
    origin_override = origin
    access_control_request_method = None
    access_control_request_headers = None
    if getattr(_http_request, "_session_id", None) and path == "/mcp":
        headers["MCP-Session-Id"] = _http_request._session_id  # type: ignore[attr-defined]
    http_method = "POST"
    session_override = None
    last_event_id = None
    if isinstance(payload, dict):
        http_method = str(payload.get("__httpMethod", "POST")).upper()
        session_override = payload.get("__sessionId")
        last_event_id = payload.get("__lastEventId")
        origin_override = payload.get("__origin", origin_override)
        access_control_request_method = payload.get("__accessControlRequestMethod")
        access_control_request_headers = payload.get("__accessControlRequestHeaders")
        payload = {key: value for key, value in payload.items() if not str(key).startswith("__")}
    if auth_token and path == "/mcp" and http_method != "OPTIONS":
        headers["Authorization"] = f"Bearer {auth_token}"
    if origin_override:
        headers["Origin"] = origin_override
    if session_override and path == "/mcp":
        headers["MCP-Session-Id"] = session_override
    if last_event_id and path == "/mcp":
        headers["Last-Event-ID"] = last_event_id
    if http_method == "OPTIONS":
        headers.pop("Content-Type", None)
        headers["Accept"] = "application/json"
        if access_control_request_method:
            headers["Access-Control-Request-Method"] = str(access_control_request_method)
        if access_control_request_headers:
            headers["Access-Control-Request-Headers"] = (
                ", ".join(access_control_request_headers)
                if isinstance(access_control_request_headers, list)
                else str(access_control_request_headers)
            )
    data = json.dumps(payload).encode("utf-8") if http_method not in {"GET", "OPTIONS"} else None
    if path in {"/health", "/ready"} and http_method == "POST":
        req = request.Request(url, data=data, headers=headers, method="POST")
    elif http_method in {"GET", "OPTIONS"} or path in {"/health", "/ready"}:
        req = request.Request(url, headers=headers, method=http_method if http_method in {"GET", "OPTIONS"} else "GET")
    else:
        req = request.Request(url, data=data, headers=headers, method=http_method)
    try:
        with request.urlopen(req, timeout=30) as response:
            content = response.read().decode("utf-8")
            content_type = response.headers.get("Content-Type", "")
            if "text/event-stream" in content_type:
                result = {"_sseBody": content}
            else:
                result = json.loads(content) if content else {}
            result["statusCode"] = response.status
            result["_headers"] = dict(response.headers.items())
            if response.headers.get("MCP-Session-Id"):
                _http_request._session_id = response.headers["MCP-Session-Id"]  # type: ignore[attr-defined]
            return result
    except error.HTTPError as exc:
        content = exc.read().decode("utf-8")
        payload_data = json.loads(content) if content else {}
        payload_data["statusCode"] = exc.code
        payload_data["_headers"] = dict(exc.headers.items())
        return payload_data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify hosted Cloud Run foundation behavior.")
    parser.add_argument("--deployment-record")
    parser.add_argument("--service-url")
    parser.add_argument("--revision-name")
    parser.add_argument("--service-name")
    parser.add_argument("--runtime-identity")
    parser.add_argument("--public-invocation-intent")
    parser.add_argument("--min-instances", type=int)
    parser.add_argument("--max-instances", type=int)
    parser.add_argument("--concurrency", type=int)
    parser.add_argument("--timeout-seconds", type=int)
    parser.add_argument("--auth-token")
    parser.add_argument("--origin")
    parser.add_argument("--evidence-file", default="artifacts/cloud-run-verification.txt")
    args = parser.parse_args(argv)

    deployment_record = {}
    runtime_settings = {}
    if args.deployment_record:
        deployment_record = json.loads(Path(args.deployment_record).read_text())
        runtime_settings = deployment_record.get("runtimeSettings", {})

    service_url = args.service_url or deployment_record.get("serviceUrl")
    revision_name = args.revision_name or deployment_record.get("revisionName")
    service_name = args.service_name or runtime_settings.get("serviceName")
    runtime_identity = args.runtime_identity or runtime_settings.get("runtimeIdentity")
    public_invocation_intent = (
        args.public_invocation_intent
        or deployment_record.get("publicInvocationIntent")
        or runtime_settings.get("publicInvocationIntent")
    )
    min_instances = args.min_instances if args.min_instances is not None else runtime_settings.get("minInstances")
    max_instances = args.max_instances if args.max_instances is not None else runtime_settings.get("maxInstances")
    concurrency = args.concurrency if args.concurrency is not None else runtime_settings.get("concurrency")
    timeout_seconds = (
        args.timeout_seconds if args.timeout_seconds is not None else runtime_settings.get("timeoutSeconds")
    )
    auth_token = args.auth_token or os.environ.get("MCP_AUTH_TOKEN")
    origin = args.origin or os.environ.get("MCP_ALLOWED_ORIGIN")

    missing = [
        name
        for name, value in (
            ("service-url", service_url),
            ("revision-name", revision_name),
            ("service-name", service_name),
            ("runtime-identity", runtime_identity),
            ("min-instances", min_instances),
            ("max-instances", max_instances),
            ("concurrency", concurrency),
            ("timeout-seconds", timeout_seconds),
        )
        if value in {None, ""}
    ]
    if missing:
        parser.error(
            "missing required verification inputs: "
            + ", ".join(missing)
            + ". Supply them directly or provide --deployment-record."
        )

    revision = HostedRevisionRecord(
        revision_name=revision_name,
        service_name=service_name,
        deployment_timestamp="unknown",
        endpoint_url=service_url,
        runtime_identity=runtime_identity,
        scaling_settings={
            "minInstances": min_instances,
            "maxInstances": max_instances,
            "concurrency": concurrency,
        },
        timeout_seconds=timeout_seconds,
        status="created",
        secret_reference_names=tuple(runtime_settings.get("secretReferenceNames", [])),
        secret_access_mode=runtime_settings.get("secretAccessMode", "env_only"),
        session_backend=runtime_settings.get("configSummary", {}).get("MCP_SESSION_BACKEND"),
        session_store_url=runtime_settings.get("configSummary", {}).get("MCP_SESSION_STORE_URL"),
        session_connectivity_model=runtime_settings.get("sessionConnectivityModel"),
    )
    _http_request._session_id = None  # type: ignore[attr-defined]
    _http_request._auth_token = auth_token  # type: ignore[attr-defined]
    _http_request._origin = origin  # type: ignore[attr-defined]
    run = run_hosted_verification(
        revision,
        requester=lambda path, payload: _http_request(service_url, path, payload),
        evidence_path=args.evidence_file,
        browser_origin=origin,
    )
    evidence_path = write_verification_evidence(Path(args.evidence_file), run)
    first_failure = next((check for check in run.checks if check.result == "fail"), None)
    print(
        json.dumps(
            {
                "overallResult": run.overall_result,
                "errorCodeContract": "numeric",
                "runtimeIdentity": revision.runtime_identity,
                "publicInvocationIntent": public_invocation_intent,
                "evidenceFile": str(evidence_path),
                "checkNames": [check.check_name for check in run.checks],
                "failureLayers": [check.failure_layer for check in run.checks if check.result == "fail"],
                "firstFailure": (
                    {
                        "checkName": first_failure.check_name,
                        "failureLayer": first_failure.failure_layer,
                        "requestReachedApplication": first_failure.request_reached_application,
                        "remediation": first_failure.remediation,
                    }
                    if first_failure
                    else None
                ),
            }
        )
    )
    return 0 if run.overall_result == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
