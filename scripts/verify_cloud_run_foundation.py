#!/usr/bin/env python3
"""Hosted verification CLI for the foundation Cloud Run deployment."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib import error, request

from mcp_server.deploy import HostedRevisionRecord, run_hosted_verification, write_verification_evidence


def _http_request(base_url: str, path: str, payload: object) -> dict:
    url = f"{base_url.rstrip('/')}{path}"
    headers = {"Content-Type": "application/json"}
    data = json.dumps(payload).encode("utf-8")
    if path in {"/healthz", "/readyz"}:
        req = request.Request(url, headers=headers, method="GET")
        body = None
    else:
        req = request.Request(url, data=data, headers=headers, method="POST")
        body = data
    try:
        with request.urlopen(req if body is None else req, timeout=30) as response:
            content = response.read().decode("utf-8")
            result = json.loads(content) if content else {}
            result["statusCode"] = response.status
            return result
    except error.HTTPError as exc:
        content = exc.read().decode("utf-8")
        payload_data = json.loads(content) if content else {}
        payload_data["statusCode"] = exc.code
        return payload_data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify hosted Cloud Run foundation behavior.")
    parser.add_argument("--service-url", required=True)
    parser.add_argument("--revision-name", required=True)
    parser.add_argument("--service-name", required=True)
    parser.add_argument("--runtime-identity", required=True)
    parser.add_argument("--min-instances", type=int, required=True)
    parser.add_argument("--max-instances", type=int, required=True)
    parser.add_argument("--concurrency", type=int, required=True)
    parser.add_argument("--timeout-seconds", type=int, required=True)
    parser.add_argument("--evidence-file", default="artifacts/cloud-run-verification.txt")
    args = parser.parse_args(argv)

    revision = HostedRevisionRecord(
        revision_name=args.revision_name,
        service_name=args.service_name,
        deployment_timestamp="unknown",
        endpoint_url=args.service_url,
        runtime_identity=args.runtime_identity,
        scaling_settings={
            "minInstances": args.min_instances,
            "maxInstances": args.max_instances,
            "concurrency": args.concurrency,
        },
        timeout_seconds=args.timeout_seconds,
        status="created",
    )
    run = run_hosted_verification(
        revision,
        requester=lambda path, payload: _http_request(args.service_url, path, payload),
        evidence_path=args.evidence_file,
    )
    evidence_path = write_verification_evidence(Path(args.evidence_file), run)
    print(json.dumps({"overallResult": run.overall_result, "evidenceFile": str(evidence_path)}))
    return 0 if run.overall_result == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
