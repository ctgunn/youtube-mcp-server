"""Deployment planning and hosted verification helpers for FND-006."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
from typing import Callable, Mapping


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean_env_value(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


@dataclass(frozen=True)
class DeploymentInputSet:
    """Validated input set required to create a hosted revision."""

    environment: str
    service_name: str
    image_reference: str
    runtime_identity: str
    region: str
    project_id: str
    secret_references: tuple[str, ...]
    config_values: Mapping[str, str]
    min_instances: int
    max_instances: int
    concurrency: int
    timeout_seconds: int

    def validate(self) -> list[str]:
        failures: list[str] = []
        if self.environment not in {"dev", "staging", "prod"}:
            failures.append("environment must be one of dev, staging, prod")
        if not self.service_name.strip():
            failures.append("service_name is required")
        if not self.image_reference.strip():
            failures.append("image_reference is required")
        if not self.runtime_identity.strip():
            failures.append("runtime_identity is required")
        if not self.region.strip():
            failures.append("region is required")
        if not self.project_id.strip():
            failures.append("project_id is required")
        if self.min_instances < 0:
            failures.append("min_instances must be >= 0")
        if self.max_instances < self.min_instances:
            failures.append("max_instances must be >= min_instances")
        if self.concurrency <= 0:
            failures.append("concurrency must be > 0")
        if self.timeout_seconds <= 0:
            failures.append("timeout_seconds must be > 0")
        required_config = {"MCP_ENVIRONMENT"}
        missing_config = sorted(key for key in required_config if not _clean_env_value(self.config_values.get(key)))
        if missing_config:
            failures.append(f"missing required config values: {', '.join(missing_config)}")
        if self.environment in {"staging", "prod"}:
            for secret_name in ("YOUTUBE_API_KEY", "MCP_AUTH_TOKEN"):
                if secret_name not in self.secret_references:
                    failures.append(f"{secret_name} secret reference is required for staging and prod")
        return failures


def deployment_input_from_mapping(values: Mapping[str, object]) -> DeploymentInputSet:
    """Build a deployment input set from shell-like values."""

    secret_refs = tuple(
        entry.strip()
        for entry in str(values.get("SECRET_REFERENCES", "")).split(",")
        if entry.strip()
    )
    config_values = {
        "MCP_ENVIRONMENT": str(values.get("MCP_ENVIRONMENT", "")).strip(),
        "MCP_SERVER_VERSION": str(values.get("MCP_SERVER_VERSION", "0.1.0")).strip() or "0.1.0",
        "MCP_BUILD_ID": str(values.get("MCP_BUILD_ID", "local")).strip() or "local",
        "MCP_BUILD_COMMIT": str(values.get("MCP_BUILD_COMMIT", "unknown")).strip() or "unknown",
        "MCP_BUILD_TIME": str(values.get("MCP_BUILD_TIME", "unknown")).strip() or "unknown",
        "MCP_SERVER_IMPLEMENTATION": str(values.get("MCP_SERVER_IMPLEMENTATION", "uvicorn")).strip() or "uvicorn",
        "MCP_ASGI_APP": str(values.get("MCP_ASGI_APP", "mcp_server.cloud_run_entrypoint:app")).strip()
        or "mcp_server.cloud_run_entrypoint:app",
        "MCP_AUTH_REQUIRED": str(values.get("MCP_AUTH_REQUIRED", "")).strip(),
        "MCP_ALLOWED_ORIGINS": str(values.get("MCP_ALLOWED_ORIGINS", "")).strip(),
        "MCP_ALLOW_ORIGINLESS_CLIENTS": str(values.get("MCP_ALLOW_ORIGINLESS_CLIENTS", "")).strip(),
    }
    return DeploymentInputSet(
        environment=str(values.get("MCP_ENVIRONMENT", "")).strip(),
        service_name=str(values.get("SERVICE_NAME", "")).strip(),
        image_reference=str(values.get("IMAGE_REFERENCE", "")).strip(),
        runtime_identity=str(values.get("SERVICE_ACCOUNT_EMAIL", "")).strip(),
        region=str(values.get("REGION", "")).strip(),
        project_id=str(values.get("PROJECT_ID", "")).strip(),
        secret_references=secret_refs,
        config_values=config_values,
        min_instances=int(values.get("MIN_INSTANCES", 0)),
        max_instances=int(values.get("MAX_INSTANCES", 1)),
        concurrency=int(values.get("CONCURRENCY", 80)),
        timeout_seconds=int(values.get("TIMEOUT_SECONDS", 300)),
    )


def build_deploy_command(settings: DeploymentInputSet) -> list[str]:
    """Build the deploy command after validating the input set."""

    failures = settings.validate()
    if failures:
        raise ValueError("; ".join(failures))

    env_vars = ",".join(f"{key}={value}" for key, value in sorted(settings.config_values.items()))
    secret_args = ",".join(f"{name}={name}:latest" for name in settings.secret_references)
    command = [
        "gcloud",
        "run",
        "deploy",
        settings.service_name,
        "--image",
        settings.image_reference,
        "--region",
        settings.region,
        "--project",
        settings.project_id,
        "--service-account",
        settings.runtime_identity,
        "--min-instances",
        str(settings.min_instances),
        "--max-instances",
        str(settings.max_instances),
        "--concurrency",
        str(settings.concurrency),
        "--timeout",
        str(settings.timeout_seconds),
        "--set-env-vars",
        env_vars,
    ]
    if secret_args:
        command.extend(["--set-secrets", secret_args])
    return command


@dataclass(frozen=True)
class RuntimeSettingsSnapshot:
    service_name: str
    environment_profile: str
    runtime_identity: str
    min_instances: int
    max_instances: int
    concurrency: int
    timeout_seconds: int
    secret_reference_names: tuple[str, ...]
    config_summary: Mapping[str, str]
    server_implementation: str = "uvicorn"
    app_module: str = "mcp_server.cloud_run_entrypoint:app"


@dataclass(frozen=True)
class DeploymentRunRecord:
    deployment_id: str
    executed_at: str
    outcome: str
    summary: str
    runtime_settings: RuntimeSettingsSnapshot
    revision_name: str | None = None
    service_url: str | None = None
    failure_stage: str | None = None
    remediation: str | None = None


def snapshot_runtime_settings(settings: DeploymentInputSet) -> RuntimeSettingsSnapshot:
    return RuntimeSettingsSnapshot(
        service_name=settings.service_name,
        environment_profile=settings.environment,
        runtime_identity=settings.runtime_identity,
        server_implementation=settings.config_values["MCP_SERVER_IMPLEMENTATION"],
        app_module=settings.config_values["MCP_ASGI_APP"],
        min_instances=settings.min_instances,
        max_instances=settings.max_instances,
        concurrency=settings.concurrency,
        timeout_seconds=settings.timeout_seconds,
        secret_reference_names=settings.secret_references,
        config_summary=dict(settings.config_values),
    )


def serialize_deployment_run(record: DeploymentRunRecord) -> dict:
    return {
        "deploymentId": record.deployment_id,
        "executedAt": record.executed_at,
        "outcome": record.outcome,
        "summary": record.summary,
        "revisionName": record.revision_name,
        "serviceUrl": record.service_url,
        "failureStage": record.failure_stage,
        "remediation": record.remediation,
        "runtimeSettings": {
            "serviceName": record.runtime_settings.service_name,
            "environmentProfile": record.runtime_settings.environment_profile,
            "runtimeIdentity": record.runtime_settings.runtime_identity,
            "serverImplementation": record.runtime_settings.server_implementation,
            "appModule": record.runtime_settings.app_module,
            "minInstances": record.runtime_settings.min_instances,
            "maxInstances": record.runtime_settings.max_instances,
            "concurrency": record.runtime_settings.concurrency,
            "timeoutSeconds": record.runtime_settings.timeout_seconds,
            "secretReferenceNames": list(record.runtime_settings.secret_reference_names),
            "configSummary": dict(record.runtime_settings.config_summary),
        },
    }


def _build_deployment_record(
    *,
    outcome: str,
    summary: str,
    settings: DeploymentInputSet,
    revision_name: str | None = None,
    service_url: str | None = None,
    failure_stage: str | None = None,
    remediation: str | None = None,
) -> DeploymentRunRecord:
    return DeploymentRunRecord(
        deployment_id=f"deploy-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        executed_at=_now_iso(),
        outcome=outcome,
        summary=summary,
        runtime_settings=snapshot_runtime_settings(settings),
        revision_name=revision_name,
        service_url=service_url,
        failure_stage=failure_stage,
        remediation=remediation,
    )


def _parse_deploy_metadata(stdout: str) -> tuple[str | None, str | None]:
    text = stdout.strip()
    if not text:
        return None, None
    payload = json.loads(text)
    if not isinstance(payload, dict):
        return None, None
    status = payload.get("status")
    metadata = payload.get("metadata")
    if not isinstance(status, dict):
        status = {}
    if not isinstance(metadata, dict):
        metadata = {}
    revision_name = (
        status.get("latestReadyRevisionName")
        or status.get("latestCreatedRevisionName")
        or payload.get("revisionName")
        or metadata.get("name")
    )
    service_url = status.get("url") or payload.get("serviceUrl") or payload.get("url")
    return revision_name, service_url


def execute_deploy_command(
    settings: DeploymentInputSet,
    *,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    gcloud_bin: str = "gcloud",
) -> DeploymentRunRecord:
    failures = settings.validate()
    if failures:
        return _build_deployment_record(
            outcome="failed",
            summary="; ".join(failures),
            settings=settings,
            failure_stage="input_validation",
            remediation="Provide all required deployment inputs before re-running the workflow.",
        )

    command = build_deploy_command(settings)
    command[0] = gcloud_bin
    command.extend(["--format", "json"])
    completed = runner(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        summary = completed.stderr.strip() or completed.stdout.strip() or "Deployment command failed."
        return _build_deployment_record(
            outcome="failed",
            summary=summary,
            settings=settings,
            failure_stage="deployment_execution",
            remediation="Inspect deploy command output, correct the failing platform input, and retry the workflow.",
        )

    revision_name, service_url = _parse_deploy_metadata(completed.stdout)
    if revision_name and service_url:
        return _build_deployment_record(
            outcome="success",
            summary="Deployment created a hosted revision and captured required metadata.",
            settings=settings,
            revision_name=revision_name,
            service_url=service_url,
        )

    return _build_deployment_record(
        outcome="incomplete",
        summary="Deployment command succeeded but required revision metadata could not be captured.",
        settings=settings,
        revision_name=revision_name,
        service_url=service_url,
        failure_stage="metadata_capture",
        remediation="Inspect the deploy output and Cloud Run service details, then re-run the workflow once revision metadata is available.",
    )


@dataclass(frozen=True)
class HostedRevisionRecord:
    revision_name: str
    service_name: str
    deployment_timestamp: str
    endpoint_url: str
    runtime_identity: str
    scaling_settings: Mapping[str, int]
    timeout_seconds: int
    status: str


@dataclass(frozen=True)
class VerificationCheckResult:
    check_name: str
    endpoint_url: str
    executed_at: str
    result: str
    summary: str
    status_code: int | None = None
    evidence_location: str | None = None


@dataclass(frozen=True)
class HostedVerificationRun:
    revision_name: str
    runtime_identity: str
    started_at: str
    completed_at: str | None
    overall_result: str
    checks: tuple[VerificationCheckResult, ...]


def serialize_verification_run(run: HostedVerificationRun) -> dict:
    return {
        "revisionName": run.revision_name,
        "runtimeIdentity": run.runtime_identity,
        "startedAt": run.started_at,
        "completedAt": run.completed_at,
        "overallResult": run.overall_result,
        "checks": [
            {
                "checkName": item.check_name,
                "endpointUrl": item.endpoint_url,
                "executedAt": item.executed_at,
                "result": item.result,
                "summary": item.summary,
                "statusCode": item.status_code,
                "evidenceLocation": item.evidence_location,
            }
            for item in run.checks
        ],
    }


Requester = Callable[[str, object], object]


def _parse_sse_events(body: bytes | str) -> list[dict[str, str]]:
    text = body.decode("utf-8") if isinstance(body, bytes) else str(body or "")
    events: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in text.splitlines():
        if not line.strip():
            if current:
                events.append(current)
                current = {}
            continue
        key, _, value = line.partition(":")
        current[key] = value.lstrip()
    if current:
        events.append(current)
    return events


def _normalize_request_result(result: object) -> dict:
    if isinstance(result, dict):
        return result

    status = getattr(result, "status", None)
    headers = getattr(result, "headers", {}) or {}
    payload = getattr(result, "payload", None)
    body = getattr(result, "body", b"")
    normalized = dict(payload or {})
    normalized["_headers"] = dict(headers)
    if status is not None:
        normalized["statusCode"] = status

    content_type = headers.get("Content-Type") or headers.get("content-type")
    if content_type == "text/event-stream":
        events = _parse_sse_events(body)
        normalized["_sseEvents"] = events
        for event in reversed(events):
            data = event.get("data", "")
            if not data:
                continue
            try:
                decoded = json.loads(data)
            except json.JSONDecodeError:
                continue
            if isinstance(decoded, dict):
                normalized.update(decoded)
                break
    return normalized


def _result_tools(payload: dict) -> list[dict]:
    result = payload.get("result")
    if isinstance(result, dict):
        tools = result.get("tools")
        if isinstance(tools, list):
            return tools
    return []


def _result_content_text(payload: dict) -> str | None:
    result = payload.get("result")
    if not isinstance(result, dict):
        return None
    content = result.get("content")
    if not isinstance(content, list) or not content:
        return None
    first = content[0]
    if not isinstance(first, dict):
        return None
    text = first.get("text")
    return text if isinstance(text, str) else None


def _result_structured_content(payload: dict):
    result = payload.get("result")
    if not isinstance(result, dict):
        return None
    content = result.get("content")
    if not isinstance(content, list) or not content:
        return None
    first = content[0]
    if not isinstance(first, dict):
        return None
    return first.get("structuredContent")


def run_hosted_verification(
    revision: HostedRevisionRecord,
    requester: Requester,
    evidence_path: str | None = None,
    baseline_tool_name: str = "server_ping",
    browser_origin: str | None = None,
    denied_browser_origin: str = "https://evil.example",
) -> HostedVerificationRun:
    """Run hosted verification in the required order."""

    started_at = _now_iso()
    checks: list[VerificationCheckResult] = []

    remediation = {
        "liveness": "Inspect the deployed revision startup logs and confirm the container is listening on the expected port.",
        "readiness": "Review runtime configuration and secret injection, then redeploy or re-run verification.",
        "initialize": "Confirm the hosted MCP endpoint is reachable and the initialize method is still supported.",
        "list-tools": "Confirm the hosted registry remains discoverable before re-running verification.",
        "session-post-continuation": "Inspect hosted POST continuation state, shared session storage, and session validation before re-running verification.",
        "session-get-continuation": "Inspect hosted GET continuation state and stream-session validation before re-running verification.",
        "session-reconnect": "Inspect hosted replay retention and reconnect cursor handling before re-running verification.",
        "session-invalid": "Inspect session-state error mapping for invalid or expired sessions before re-running verification.",
        "browser-preflight-approved": "Inspect browser preflight routing and CORS allow-header generation before re-running verification.",
        "browser-request-approved": "Inspect approved-origin response-header shaping and hosted MCP browser compatibility before re-running verification.",
        "browser-origin-denied": "Inspect the browser origin allowlist and denial mapping before re-running verification.",
        "browser-request-unsupported": "Inspect browser unsupported-route, method, and header handling before re-running verification.",
    }
    stage = {
        "liveness": "deployment-time",
        "readiness": "readiness-time",
        "initialize": "MCP-time",
        "list-tools": "MCP-time",
        "session-post-continuation": "MCP-time",
        "session-get-continuation": "MCP-time",
        "session-reconnect": "MCP-time",
        "session-invalid": "MCP-time",
        "browser-preflight-approved": "browser-time",
        "browser-request-approved": "browser-time",
        "browser-origin-denied": "browser-time",
        "browser-request-unsupported": "browser-time",
    }

    def _append(check_name: str, payload: dict, expected: Callable[[dict], bool], summary: str) -> bool:
        ok = expected(payload)
        result_summary = summary
        if not ok:
            result_summary = f"{stage[check_name]} failure during {check_name}. {remediation[check_name]}"
        checks.append(
            VerificationCheckResult(
                check_name=check_name,
                endpoint_url=revision.endpoint_url,
                executed_at=_now_iso(),
                result="pass" if ok else "fail",
                summary=result_summary,
                status_code=payload.get("statusCode"),
                evidence_location=evidence_path,
            )
        )
        return ok

    health_payload = _normalize_request_result(requester("/health", {}))
    if not _append(
        "liveness",
        health_payload,
        lambda payload: payload.get("status") == "ok",
        "Hosted liveness endpoint returned healthy status.",
    ):
        return HostedVerificationRun(revision.revision_name, revision.runtime_identity, started_at, _now_iso(), "fail", tuple(checks))

    ready_payload = _normalize_request_result(requester("/ready", {}))
    if not _append(
        "readiness",
        ready_payload,
        lambda payload: payload.get("status") == "ready",
        "Hosted readiness endpoint returned ready status.",
    ):
        return HostedVerificationRun(revision.revision_name, revision.runtime_identity, started_at, _now_iso(), "fail", tuple(checks))

    initialize_payload = _normalize_request_result(
        requester(
        "/mcp",
        {
            "jsonrpc": "2.0",
            "id": "verify-init",
            "method": "initialize",
            "params": {"clientInfo": {"name": "cloud-run-verifier", "version": "1.0.0"}},
        },
        )
    )
    if not _append(
        "initialize",
        initialize_payload,
        lambda payload: isinstance(payload.get("result"), dict) and "capabilities" in payload.get("result", {}),
        "Hosted MCP initialize returned declared capabilities.",
    ):
        return HostedVerificationRun(revision.revision_name, revision.runtime_identity, started_at, _now_iso(), "fail", tuple(checks))

    list_payload = _normalize_request_result(
        requester("/mcp", {"jsonrpc": "2.0", "id": "verify-list", "method": "tools/list", "params": {}})
    )
    if not _append(
        "list-tools",
        list_payload,
        lambda payload: {"search", "fetch"}.issubset({tool.get("name") for tool in _result_tools(payload)}),
        "Hosted MCP tool discovery returned the deep research tool set.",
    ):
        return HostedVerificationRun(revision.revision_name, revision.runtime_identity, started_at, _now_iso(), "fail", tuple(checks))

    post_continuation_payload = _normalize_request_result(
        requester(
        "/mcp",
        {
            "jsonrpc": "2.0",
            "id": "verify-post-continuation",
            "method": "tools/list",
            "params": {},
        },
        )
    )
    if not _append(
        "session-post-continuation",
        post_continuation_payload,
        lambda payload: isinstance(payload.get("result"), dict) and isinstance(payload.get("result", {}).get("tools"), list),
        "Hosted MCP POST continuation succeeded with the initialized session.",
    ):
        return HostedVerificationRun(revision.revision_name, revision.runtime_identity, started_at, _now_iso(), "fail", tuple(checks))

    get_continuation_payload = _normalize_request_result(
        requester(
            "/mcp",
            {
                "__httpMethod": "GET",
            },
        )
    )
    if not _append(
        "session-get-continuation",
        get_continuation_payload,
        lambda payload: isinstance(payload.get("_sseEvents"), list) and len(payload.get("_sseEvents", [])) >= 1,
        "Hosted MCP GET continuation succeeded for the active session.",
    ):
        return HostedVerificationRun(revision.revision_name, revision.runtime_identity, started_at, _now_iso(), "fail", tuple(checks))

    replay_seed_payload = _normalize_request_result(
        requester(
            "/mcp",
            {
                "jsonrpc": "2.0",
                "id": "verify-replay-seed",
                "method": "tools/call",
                "params": {"name": baseline_tool_name, "arguments": {}},
            },
        )
    )
    replay_events = replay_seed_payload.get("_sseEvents", [])
    replay_cursor = replay_events[0]["id"] if replay_events else None
    reconnect_payload = _normalize_request_result(
        requester(
            "/mcp",
            {
                "__httpMethod": "GET",
                "__lastEventId": replay_cursor,
            },
        )
    )
    if not _append(
        "session-reconnect",
        reconnect_payload,
        lambda payload: isinstance(payload.get("_sseEvents"), list)
        and any('"result"' in event.get("data", "") for event in payload.get("_sseEvents", [])),
        "Hosted MCP reconnect replayed retained events for the active session.",
    ):
        return HostedVerificationRun(revision.revision_name, revision.runtime_identity, started_at, _now_iso(), "fail", tuple(checks))

    invalid_payload = _normalize_request_result(
        requester(
            "/mcp",
            {
                "__httpMethod": "GET",
                "__sessionId": "missing-session",
            },
        )
    )
    _append(
        "session-invalid",
        invalid_payload,
        lambda payload: payload.get("statusCode") == 404 and payload.get("error", {}).get("code") == "RESOURCE_NOT_FOUND",
        "Hosted MCP invalid-session handling returned the expected session-state failure.",
    )

    if browser_origin:
        approved_preflight_payload = _normalize_request_result(
            requester(
                "/mcp",
                {
                    "__httpMethod": "OPTIONS",
                    "__origin": browser_origin,
                    "__accessControlRequestMethod": "POST",
                    "__accessControlRequestHeaders": ["authorization", "content-type"],
                },
            )
        )
        _append(
            "browser-preflight-approved",
            approved_preflight_payload,
            lambda payload: payload.get("statusCode") == 204
            and payload.get("_headers", {}).get("Access-Control-Allow-Origin") == browser_origin,
            "Approved browser-origin preflight returned the documented allow headers.",
        )

        approved_browser_request_payload = _normalize_request_result(
            requester(
                "/mcp",
                {
                    "__origin": browser_origin,
                    "jsonrpc": "2.0",
                    "id": "verify-browser-list",
                    "method": "tools/list",
                    "params": {},
                },
            )
        )
        _append(
            "browser-request-approved",
            approved_browser_request_payload,
            lambda payload: payload.get("statusCode") == 200
            and payload.get("_headers", {}).get("Access-Control-Allow-Origin") == browser_origin
            and "MCP-Session-Id" in payload.get("_headers", {}).get("Access-Control-Expose-Headers", ""),
            "Approved browser-origin hosted MCP request returned the documented browser response headers.",
        )

        denied_browser_payload = _normalize_request_result(
            requester(
                "/mcp",
                {
                    "__httpMethod": "OPTIONS",
                    "__origin": denied_browser_origin,
                    "__accessControlRequestMethod": "POST",
                    "__accessControlRequestHeaders": ["authorization", "content-type"],
                },
            )
        )
        _append(
            "browser-origin-denied",
            denied_browser_payload,
            lambda payload: payload.get("statusCode") == 403 and payload.get("error", {}).get("code") == "ORIGIN_DENIED",
            "Denied browser-origin preflight returned the documented origin denial.",
        )

        unsupported_browser_payload = _normalize_request_result(
            requester(
                "/ready",
                {
                    "__httpMethod": "OPTIONS",
                    "__origin": browser_origin,
                    "__accessControlRequestMethod": "GET",
                },
            )
        )
        _append(
            "browser-request-unsupported",
            unsupported_browser_payload,
            lambda payload: payload.get("statusCode") == 405
            and payload.get("error", {}).get("code") == "UNSUPPORTED_BROWSER_ROUTE",
            "Unsupported browser request pattern returned the documented denial.",
        )
    overall = "pass" if all(item.result == "pass" for item in checks) else "fail"
    return HostedVerificationRun(revision.revision_name, revision.runtime_identity, started_at, _now_iso(), overall, tuple(checks))


def write_verification_evidence(destination: str | Path, run: HostedVerificationRun) -> Path:
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = serialize_verification_run(run)
    lines = [
        f"revisionName: {payload['revisionName']}",
        f"runtimeIdentity: {payload['runtimeIdentity']}",
        f"startedAt: {payload['startedAt']}",
        f"completedAt: {payload['completedAt']}",
        f"overallResult: {payload['overallResult']}",
        "checks:",
    ]
    for check in payload["checks"]:
        lines.extend(
            [
                f"  - checkName: {check['checkName']}",
                f"    result: {check['result']}",
                f"    summary: {check['summary']}",
                f"    endpointUrl: {check['endpointUrl']}",
                f"    executedAt: {check['executedAt']}",
            ]
        )
    path.write_text("\n".join(lines) + "\n")
    return path
