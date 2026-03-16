#!/usr/bin/env python3
"""Hosted verification CLI for the foundation Cloud Run deployment.

The verifier preserves the hosted streamable transport while validating
protocol-native MCP request and response bodies.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib import error, request

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mcp_server.deploy import HostedRevisionRecord, run_hosted_verification, write_verification_evidence


def _http_request(base_url: str, path: str, payload: object) -> dict:
    if not hasattr(_http_request, "_session_id"):
        _http_request._session_id = None  # type: ignore[attr-defined]
    url = f"{base_url.rstrip('/')}{path}"
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    if getattr(_http_request, "_session_id", None) and path == "/mcp":
        headers["MCP-Session-Id"] = _http_request._session_id  # type: ignore[attr-defined]
    data = json.dumps(payload).encode("utf-8")
    if path in {"/health", "/ready"}:
        req = request.Request(url, headers=headers, method="GET")
        body = None
    else:
        req = request.Request(url, data=data, headers=headers, method="POST")
        body = data
    try:
        with request.urlopen(req if body is None else req, timeout=30) as response:
            content = response.read().decode("utf-8")
            content_type = response.headers.get("Content-Type", "")
            if "text/event-stream" in content_type:
                result = {"_sseBody": content}
            else:
                result = json.loads(content) if content else {}
            result["statusCode"] = response.status
            if response.headers.get("MCP-Session-Id"):
                _http_request._session_id = response.headers["MCP-Session-Id"]  # type: ignore[attr-defined]
            return result
    except error.HTTPError as exc:
        content = exc.read().decode("utf-8")
        payload_data = json.loads(content) if content else {}
        payload_data["statusCode"] = exc.code
        return payload_data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify hosted Cloud Run foundation behavior.")
    parser.add_argument("--deployment-record")
    parser.add_argument("--service-url")
    parser.add_argument("--revision-name")
    parser.add_argument("--service-name")
    parser.add_argument("--runtime-identity")
    parser.add_argument("--min-instances", type=int)
    parser.add_argument("--max-instances", type=int)
    parser.add_argument("--concurrency", type=int)
    parser.add_argument("--timeout-seconds", type=int)
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
    min_instances = args.min_instances if args.min_instances is not None else runtime_settings.get("minInstances")
    max_instances = args.max_instances if args.max_instances is not None else runtime_settings.get("maxInstances")
    concurrency = args.concurrency if args.concurrency is not None else runtime_settings.get("concurrency")
    timeout_seconds = (
        args.timeout_seconds if args.timeout_seconds is not None else runtime_settings.get("timeoutSeconds")
    )

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
    )
    _http_request._session_id = None  # type: ignore[attr-defined]
    run = run_hosted_verification(
        revision,
        requester=lambda path, payload: _http_request(service_url, path, payload),
        evidence_path=args.evidence_file,
    )
    evidence_path = write_verification_evidence(Path(args.evidence_file), run)
    print(json.dumps({"overallResult": run.overall_result, "evidenceFile": str(evidence_path)}))
    return 0 if run.overall_result == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
