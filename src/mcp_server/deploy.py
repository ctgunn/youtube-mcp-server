"""Deployment planning and hosted verification helpers for FND-006."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
from typing import Callable, Mapping

from mcp_server.infrastructure_contract import is_supported_public_invocation_intent


def _now_iso() -> str:
    """Return the current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def _clean_env_value(value: object) -> str | None:
    """Normalize a shell-like value to a stripped string or ``None``."""
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
    public_invocation_intent: str
    secret_references: tuple[str, ...]
    config_values: Mapping[str, str]
    min_instances: int
    max_instances: int
    concurrency: int
    timeout_seconds: int
    session_network_reference: str = ""
    session_subnet_reference: str = ""
    session_connector_reference: str = ""

    def validate(self) -> list[str]:
        """Validate the deployment input set and return any failure messages."""
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
        if not is_supported_public_invocation_intent(self.public_invocation_intent):
            failures.append("public_invocation_intent must be one of public_remote_mcp, private_only")
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
        if self.config_values.get("MCP_SESSION_BACKEND") == "redis" and not _clean_env_value(
            self.config_values.get("MCP_SESSION_STORE_URL")
        ):
            failures.append("MCP_SESSION_STORE_URL is required when MCP_SESSION_BACKEND=redis")
        if self.config_values.get("MCP_SESSION_BACKEND") == "redis":
            if not _clean_env_value(self.session_network_reference):
                failures.append("session_network_reference is required when MCP_SESSION_BACKEND=redis")
            if not _clean_env_value(self.session_subnet_reference):
                failures.append("session_subnet_reference is required when MCP_SESSION_BACKEND=redis")
            if not _clean_env_value(self.session_connector_reference):
                failures.append("session_connector_reference is required when MCP_SESSION_BACKEND=redis")
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
        "MCP_SECRET_ACCESS_MODE": str(values.get("MCP_SECRET_ACCESS_MODE", "")).strip(),
        "MCP_SECRET_REFERENCE_NAMES": str(values.get("MCP_SECRET_REFERENCE_NAMES", values.get("SECRET_REFERENCES", ""))).strip(),
        "PUBLIC_INVOCATION_INTENT": str(values.get("PUBLIC_INVOCATION_INTENT", "private_only")).strip() or "private_only",
        "MCP_AUTH_REQUIRED": str(values.get("MCP_AUTH_REQUIRED", "")).strip(),
        "MCP_ALLOWED_ORIGINS": str(values.get("MCP_ALLOWED_ORIGINS", "")).strip(),
        "MCP_ALLOW_ORIGINLESS_CLIENTS": str(values.get("MCP_ALLOW_ORIGINLESS_CLIENTS", "")).strip(),
        "MCP_SESSION_BACKEND": str(values.get("MCP_SESSION_BACKEND", "")).strip(),
        "MCP_SESSION_STORE_URL": str(values.get("MCP_SESSION_STORE_URL", "")).strip(),
        "MCP_SESSION_CONNECTIVITY_MODEL": str(values.get("MCP_SESSION_CONNECTIVITY_MODEL", "")).strip(),
        "MCP_SESSION_DURABILITY_REQUIRED": str(values.get("MCP_SESSION_DURABILITY_REQUIRED", "")).strip(),
        "MCP_SESSION_TTL_SECONDS": str(values.get("MCP_SESSION_TTL_SECONDS", "")).strip(),
        "MCP_SESSION_REPLAY_TTL_SECONDS": str(values.get("MCP_SESSION_REPLAY_TTL_SECONDS", "")).strip(),
    }
    return DeploymentInputSet(
        environment=str(values.get("MCP_ENVIRONMENT", "")).strip(),
        service_name=str(values.get("SERVICE_NAME", "")).strip(),
        image_reference=str(values.get("IMAGE_REFERENCE", "")).strip(),
        runtime_identity=str(values.get("SERVICE_ACCOUNT_EMAIL", "")).strip(),
        region=str(values.get("REGION", "")).strip(),
        project_id=str(values.get("PROJECT_ID", "")).strip(),
        public_invocation_intent=str(values.get("PUBLIC_INVOCATION_INTENT", "private_only")).strip() or "private_only",
        secret_references=secret_refs,
        session_network_reference=str(values.get("MCP_SESSION_NETWORK_REFERENCE", "")).strip(),
        session_subnet_reference=str(values.get("MCP_SESSION_SUBNET_REFERENCE", "")).strip(),
        session_connector_reference=str(values.get("MCP_SESSION_CONNECTOR_REFERENCE", "")).strip(),
        config_values=config_values,
        min_instances=int(values.get("MIN_INSTANCES", 0)),
        max_instances=int(values.get("MAX_INSTANCES", 1)),
        concurrency=int(values.get("CONCURRENCY", 80)),
        timeout_seconds=int(values.get("TIMEOUT_SECONDS", 300)),
    )


IAC_OUTPUT_ALIASES = {
    "PROJECT_ID": ("PROJECT_ID", "project_id"),
    "REGION": ("REGION", "region"),
    "MCP_ENVIRONMENT": ("MCP_ENVIRONMENT", "environment", "mcp_environment"),
    "SERVICE_NAME": ("SERVICE_NAME", "service_name"),
    "SERVICE_ACCOUNT_EMAIL": ("SERVICE_ACCOUNT_EMAIL", "service_account_email"),
    "PUBLIC_INVOCATION_INTENT": ("PUBLIC_INVOCATION_INTENT", "public_invocation_intent"),
    "MCP_SECRET_ACCESS_MODE": ("MCP_SECRET_ACCESS_MODE", "mcp_secret_access_mode", "secret_access_mode"),
    "MCP_SECRET_REFERENCE_NAMES": ("MCP_SECRET_REFERENCE_NAMES", "mcp_secret_reference_names"),
    "MCP_AUTH_REQUIRED": ("MCP_AUTH_REQUIRED", "mcp_auth_required"),
    "MCP_ALLOWED_ORIGINS": ("MCP_ALLOWED_ORIGINS", "mcp_allowed_origins"),
    "MCP_ALLOW_ORIGINLESS_CLIENTS": ("MCP_ALLOW_ORIGINLESS_CLIENTS", "mcp_allow_originless_clients"),
    "MCP_SESSION_BACKEND": ("MCP_SESSION_BACKEND", "mcp_session_backend", "session_backend"),
    "MCP_SESSION_STORE_URL": ("MCP_SESSION_STORE_URL", "mcp_session_store_url", "session_store_url"),
    "MCP_SESSION_CONNECTIVITY_MODEL": (
        "MCP_SESSION_CONNECTIVITY_MODEL",
        "mcp_session_connectivity_model",
        "session_connectivity_model",
    ),
    "MCP_SESSION_NETWORK_REFERENCE": (
        "MCP_SESSION_NETWORK_REFERENCE",
        "mcp_session_network_reference",
        "session_network_reference",
    ),
    "MCP_SESSION_SUBNET_REFERENCE": (
        "MCP_SESSION_SUBNET_REFERENCE",
        "mcp_session_subnet_reference",
        "session_subnet_reference",
    ),
    "MCP_SESSION_CONNECTOR_REFERENCE": (
        "MCP_SESSION_CONNECTOR_REFERENCE",
        "mcp_session_connector_reference",
        "session_connector_reference",
    ),
    "MCP_SESSION_DURABILITY_REQUIRED": (
        "MCP_SESSION_DURABILITY_REQUIRED",
        "mcp_session_durability_required",
        "session_durability_required",
    ),
    "MCP_SESSION_TTL_SECONDS": ("MCP_SESSION_TTL_SECONDS", "mcp_session_ttl_seconds", "session_ttl_seconds"),
    "MCP_SESSION_REPLAY_TTL_SECONDS": (
        "MCP_SESSION_REPLAY_TTL_SECONDS",
        "mcp_session_replay_ttl_seconds",
        "session_replay_ttl_seconds",
    ),
    "MIN_INSTANCES": ("MIN_INSTANCES", "min_instances"),
    "MAX_INSTANCES": ("MAX_INSTANCES", "max_instances"),
    "CONCURRENCY": ("CONCURRENCY", "concurrency"),
    "TIMEOUT_SECONDS": ("TIMEOUT_SECONDS", "timeout_seconds"),
    "SECRET_REFERENCES": ("SECRET_REFERENCES", "secret_reference_names", "secret_references"),
}


def load_iac_outputs_file(path: str | Path) -> dict:
    """Load a Terraform-style outputs document from disk."""
    payload = json.loads(Path(path).read_text())
    if isinstance(payload, dict) and isinstance(payload.get("outputs"), dict):
        return payload["outputs"]
    if not isinstance(payload, dict):
        raise ValueError("IaC outputs file must contain a JSON object.")
    return payload


def _normalize_iac_value(value: object) -> object:
    """Extract the raw value from a Terraform output record when needed."""
    if isinstance(value, dict) and "value" in value:
        return value["value"]
    return value


def iac_outputs_to_mapping(outputs: Mapping[str, object]) -> dict[str, str]:
    """Normalize IaC outputs into environment-style deployment inputs."""
    resolved: dict[str, str] = {}
    for env_key, aliases in IAC_OUTPUT_ALIASES.items():
        for alias in aliases:
            if alias not in outputs:
                continue
            value = _normalize_iac_value(outputs[alias])
            if value is None:
                continue
            if isinstance(value, bool):
                resolved[env_key] = "true" if value else "false"
            elif isinstance(value, (list, tuple)):
                resolved[env_key] = ",".join(str(item) for item in value if str(item).strip())
            else:
                text = str(value).strip()
                if text:
                    resolved[env_key] = text
            break
    return resolved


def merge_deployment_values(
    base_values: Mapping[str, object],
    explicit_values: Mapping[str, object],
) -> dict[str, object]:
    """Merge base deployment values with explicit non-empty overrides."""
    merged: dict[str, object] = dict(base_values)
    for key, value in explicit_values.items():
        if value is None:
            continue
        text = str(value).strip()
        if text:
            merged[key] = text
    return merged


def deployment_input_from_iac_outputs(
    outputs: Mapping[str, object],
    *,
    image_reference: str,
    explicit_values: Mapping[str, object] | None = None,
) -> DeploymentInputSet:
    """Build deployment inputs from IaC outputs and explicit overrides."""
    merged: dict[str, object] = merge_deployment_values(
        iac_outputs_to_mapping(outputs),
        {"IMAGE_REFERENCE": image_reference, **dict(explicit_values or {})},
    )
    return deployment_input_from_mapping(merged)


def build_deploy_command(settings: DeploymentInputSet) -> list[str]:
    """Build the deploy command after validating the input set."""

    failures = settings.validate()
    if failures:
        raise ValueError("; ".join(failures))

    # Use a custom delimiter so gcloud can parse values that themselves contain commas.
    delimiter = "^@@^"
    env_vars = delimiter + "@@".join(f"{key}={value}" for key, value in sorted(settings.config_values.items()))
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
    """Capture normalized runtime settings recorded for a deployment."""

    service_name: str
    environment_profile: str
    runtime_identity: str
    min_instances: int
    max_instances: int
    concurrency: int
    timeout_seconds: int
    secret_reference_names: tuple[str, ...]
    config_summary: Mapping[str, str]
    public_invocation_intent: str = "private_only"
    server_implementation: str = "uvicorn"
    app_module: str = "mcp_server.cloud_run_entrypoint:app"
    secret_access_mode: str = "env_only"
    session_connectivity_model: str = "local_process"
    session_network_reference: str = ""
    session_subnet_reference: str = ""
    session_connector_reference: str = ""


@dataclass(frozen=True)
class DeploymentRunRecord:
    """Capture the outcome of one deploy command execution."""

    deployment_id: str
    executed_at: str
    outcome: str
    summary: str
    runtime_settings: RuntimeSettingsSnapshot
    revision_name: str | None = None
    service_url: str | None = None
    failure_stage: str | None = None
    remediation: str | None = None
    public_invocation_intent: str = "private_only"


WORKFLOW_STAGE_ORDER = (
    "quality_gate",
    "image_publish",
    "infrastructure_reconcile",
    "terraform_output_export",
    "deploy",
    "hosted_verification",
)


@dataclass(frozen=True)
class HostedDeploymentWorkflowStage:
    """Describe one stage in the hosted deployment workflow."""

    stage_name: str
    result: str
    summary: str
    artifact_path: str | None = None
    failure_boundary: str | None = None


@dataclass(frozen=True)
class BootstrapPrerequisite:
    """Describe one prerequisite required before hosted deployment can proceed."""

    name: str
    owner: str
    required_for_stage: str
    description: str


BOOTSTRAP_PREREQUISITES = (
    BootstrapPrerequisite(
        name="GCP_PROJECT_ID",
        owner="automation",
        required_for_stage="infrastructure_reconcile",
        description="Hosted project identifier used for Terraform and deploy commands.",
    ),
    BootstrapPrerequisite(
        name="GCP_REGION",
        owner="automation",
        required_for_stage="infrastructure_reconcile",
        description="Hosted region used for Terraform and deploy commands.",
    ),
    BootstrapPrerequisite(
        name="GCP_WORKLOAD_IDENTITY_PROVIDER",
        owner="automation",
        required_for_stage="quality_gate",
        description="Repository automation identity used to authenticate to GCP without static credentials.",
    ),
    BootstrapPrerequisite(
        name="GCP_SERVICE_ACCOUNT",
        owner="automation",
        required_for_stage="quality_gate",
        description="Runtime automation identity used for Terraform and deployment actions.",
    ),
    BootstrapPrerequisite(
        name="GCP_ARTIFACT_REGISTRY_REPOSITORY",
        owner="automation",
        required_for_stage="image_publish",
        description="Artifact destination used to publish the current application image.",
    ),
    BootstrapPrerequisite(
        name="GCP_TERRAFORM_VAR_FILE",
        owner="automation",
        required_for_stage="infrastructure_reconcile",
        description="Terraform variable file that defines the target hosted environment inputs.",
    ),
    BootstrapPrerequisite(
        name="YOUTUBE_API_KEY",
        owner="operator",
        required_for_stage="deploy",
        description="Required hosted secret value that must be populated outside repository automation.",
    ),
    BootstrapPrerequisite(
        name="MCP_AUTH_TOKEN",
        owner="operator",
        required_for_stage="hosted_verification",
        description="Required hosted bearer-token secret that must be populated outside repository automation.",
    ),
)


def snapshot_runtime_settings(settings: DeploymentInputSet) -> RuntimeSettingsSnapshot:
    """Snapshot deployment inputs into the runtime-settings evidence shape."""
    return RuntimeSettingsSnapshot(
        service_name=settings.service_name,
        environment_profile=settings.environment,
        runtime_identity=settings.runtime_identity,
        public_invocation_intent=settings.public_invocation_intent,
        server_implementation=settings.config_values["MCP_SERVER_IMPLEMENTATION"],
        app_module=settings.config_values["MCP_ASGI_APP"],
        secret_access_mode=settings.config_values.get("MCP_SECRET_ACCESS_MODE") or "env_only",
        session_connectivity_model=settings.config_values.get("MCP_SESSION_CONNECTIVITY_MODEL") or "local_process",
        session_network_reference=settings.session_network_reference,
        session_subnet_reference=settings.session_subnet_reference,
        session_connector_reference=settings.session_connector_reference,
        min_instances=settings.min_instances,
        max_instances=settings.max_instances,
        concurrency=settings.concurrency,
        timeout_seconds=settings.timeout_seconds,
        secret_reference_names=settings.secret_references,
        config_summary=dict(settings.config_values),
    )


def serialize_deployment_run(record: DeploymentRunRecord) -> dict:
    """Serialize a deployment run record into the public artifact shape."""
    return {
        "deploymentId": record.deployment_id,
        "executedAt": record.executed_at,
        "outcome": record.outcome,
        "summary": record.summary,
        "publicInvocationIntent": record.public_invocation_intent,
        "revisionName": record.revision_name,
        "serviceUrl": record.service_url,
        "connectionPoint": record.service_url,
        "failureStage": record.failure_stage,
        "remediation": record.remediation,
        "runtimeSettings": {
            "serviceName": record.runtime_settings.service_name,
            "environmentProfile": record.runtime_settings.environment_profile,
            "runtimeIdentity": record.runtime_settings.runtime_identity,
            "publicInvocationIntent": record.runtime_settings.public_invocation_intent,
            "serverImplementation": record.runtime_settings.server_implementation,
            "appModule": record.runtime_settings.app_module,
            "secretAccessMode": record.runtime_settings.secret_access_mode,
            "sessionConnectivityModel": record.runtime_settings.session_connectivity_model,
            "sessionNetworkReference": record.runtime_settings.session_network_reference,
            "sessionSubnetReference": record.runtime_settings.session_subnet_reference,
            "sessionConnectorReference": record.runtime_settings.session_connector_reference,
            "minInstances": record.runtime_settings.min_instances,
            "maxInstances": record.runtime_settings.max_instances,
            "concurrency": record.runtime_settings.concurrency,
            "timeoutSeconds": record.runtime_settings.timeout_seconds,
            "secretReferenceNames": list(record.runtime_settings.secret_reference_names),
            "configSummary": dict(record.runtime_settings.config_summary),
        },
    }


def serialize_workflow_stage(record: HostedDeploymentWorkflowStage) -> dict[str, object]:
    """Serialize one workflow stage for workflow reporting artifacts."""
    failure_boundary = record.failure_boundary
    if failure_boundary is None and record.result != "pass":
        failure_boundary = classify_bootstrap_failure(record.stage_name, record.summary)
    return {
        "stageName": record.stage_name,
        "result": record.result,
        "summary": record.summary,
        "artifactPath": record.artifact_path,
        "failureBoundary": failure_boundary,
    }


def workflow_overall_result(stages: tuple[HostedDeploymentWorkflowStage, ...] | list[HostedDeploymentWorkflowStage]) -> str:
    """Derive the overall workflow result from individual stages."""
    if any(stage.result == "fail" for stage in stages):
        return "fail"
    if any(stage.result == "incomplete" for stage in stages):
        return "incomplete"
    if stages and all(stage.result == "pass" for stage in stages):
        return "pass"
    return "incomplete"


def classify_bootstrap_failure(stage_name: str, summary: str = "") -> str | None:
    """Map a failing workflow stage to a higher-level failure boundary."""
    normalized_stage = (stage_name or "").strip()
    normalized_summary = (summary or "").strip().lower()
    if not normalized_stage:
        return None
    if normalized_stage == "quality_gate":
        return "bootstrap_input_failure"
    if normalized_stage in {"infrastructure_reconcile", "terraform_output_export"}:
        if "bootstrap" in normalized_summary or "network" in normalized_summary or normalized_stage == "infrastructure_reconcile":
            return "network_reconcile_failure"
        return "network_reconcile_failure"
    if normalized_stage == "deploy":
        return "deployment_failure"
    if normalized_stage == "hosted_verification":
        return "hosted_verification_failure"
    return None


def serialize_workflow_run(
    branch_name: str,
    revision_ref: str,
    stages: tuple[HostedDeploymentWorkflowStage, ...] | list[HostedDeploymentWorkflowStage],
) -> dict[str, object]:
    """Serialize the full hosted deployment workflow summary."""
    ordered_stage_names = [stage.stage_name for stage in stages]
    first_failed_stage = next((stage for stage in stages if stage.result != "pass"), None)
    first_failed = first_failed_stage.stage_name if first_failed_stage else None
    first_failed_boundary = (
        classify_bootstrap_failure(first_failed_stage.stage_name, first_failed_stage.summary)
        if first_failed_stage
        else None
    )
    return {
        "branchName": branch_name,
        "revisionRef": revision_ref,
        "stageOrder": list(WORKFLOW_STAGE_ORDER),
        "stageNames": ordered_stage_names,
        "overallResult": workflow_overall_result(stages),
        "firstFailedStage": first_failed,
        "firstFailedBoundary": first_failed_boundary,
        "artifacts": {
            stage.stage_name: stage.artifact_path
            for stage in stages
            if stage.artifact_path
        },
        "stages": [serialize_workflow_stage(stage) for stage in stages],
    }


def load_json_artifact(path: str | Path) -> dict:
    """Load a JSON workflow artifact from disk."""
    payload = json.loads(Path(path).read_text())
    if not isinstance(payload, dict):
        raise ValueError("Workflow artifact must contain a JSON object.")
    return payload


def collect_missing_bootstrap_prerequisites(values: Mapping[str, object]) -> tuple[BootstrapPrerequisite, ...]:
    """Return the declared bootstrap prerequisites that are still missing."""
    missing: list[BootstrapPrerequisite] = []
    for prerequisite in BOOTSTRAP_PREREQUISITES:
        value = values.get(prerequisite.name)
        if value is None:
            missing.append(prerequisite)
            continue
        if isinstance(value, bool):
            if not value:
                missing.append(prerequisite)
            continue
        if not str(value).strip():
            missing.append(prerequisite)
    return tuple(missing)


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
    """Build a deployment run record from execution inputs and outcome."""
    return DeploymentRunRecord(
        deployment_id=f"deploy-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        executed_at=_now_iso(),
        outcome=outcome,
        summary=summary,
        runtime_settings=snapshot_runtime_settings(settings),
        public_invocation_intent=settings.public_invocation_intent,
        revision_name=revision_name,
        service_url=service_url,
        failure_stage=failure_stage,
        remediation=remediation,
    )


def _parse_deploy_metadata(stdout: str) -> tuple[str | None, str | None]:
    """Parse revision metadata from ``gcloud run deploy`` JSON output."""
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
    """Execute the deploy command and normalize the resulting run record."""
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
    """Describe the hosted revision that verification should inspect."""

    revision_name: str
    service_name: str
    deployment_timestamp: str
    endpoint_url: str
    runtime_identity: str
    scaling_settings: Mapping[str, int]
    timeout_seconds: int
    status: str
    secret_reference_names: tuple[str, ...] = ()
    secret_access_mode: str = "env_only"
    session_backend: str | None = None
    session_store_url: str | None = None
    session_connectivity_model: str | None = None
    session_network_reference: str | None = None
    session_subnet_reference: str | None = None
    session_connector_reference: str | None = None


@dataclass(frozen=True)
class VerificationCheckResult:
    """Describe the outcome of one hosted verification check."""

    check_name: str
    endpoint_url: str
    executed_at: str
    result: str
    summary: str
    status_code: int | None = None
    evidence_location: str | None = None
    failure_layer: str | None = None
    request_reached_application: bool | None = None
    remediation: str | None = None


@dataclass(frozen=True)
class HostedVerificationRun:
    """Capture the aggregate outcome of hosted verification."""

    revision_name: str
    runtime_identity: str
    started_at: str
    completed_at: str | None
    overall_result: str
    checks: tuple[VerificationCheckResult, ...]
    session_network_reference: str | None = None
    session_subnet_reference: str | None = None
    session_connector_reference: str | None = None


def serialize_verification_run(run: HostedVerificationRun) -> dict:
    """Serialize hosted verification results into an evidence payload."""
    return {
        "revisionName": run.revision_name,
        "runtimeIdentity": run.runtime_identity,
        "startedAt": run.started_at,
        "completedAt": run.completed_at,
        "overallResult": run.overall_result,
        "sessionNetworkReference": run.session_network_reference,
        "sessionSubnetReference": run.session_subnet_reference,
        "sessionConnectorReference": run.session_connector_reference,
        "checks": [
            {
                "checkName": item.check_name,
                "endpointUrl": item.endpoint_url,
                "executedAt": item.executed_at,
                "result": item.result,
                "summary": item.summary,
                "statusCode": item.status_code,
                "evidenceLocation": item.evidence_location,
                "failureLayer": item.failure_layer,
                "requestReachedApplication": item.request_reached_application,
                "remediation": item.remediation,
            }
            for item in run.checks
        ],
    }


Requester = Callable[[str, object], object]


def _parse_sse_events(body: bytes | str) -> list[dict[str, str]]:
    """Parse an SSE response body into event dictionaries."""
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
    """Normalize HTTP requester output into one verification payload shape."""
    if isinstance(result, dict):
        normalized = dict(result)
        headers = normalized.get("_headers", {}) or {}
        content_type = None
        if isinstance(headers, dict):
            content_type = headers.get("Content-Type") or headers.get("content-type")
        if content_type == "text/event-stream" and isinstance(normalized.get("_sseBody"), str):
            events = _parse_sse_events(normalized["_sseBody"])
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
    """Extract tool descriptors from a verification response payload."""
    result = payload.get("result")
    if isinstance(result, dict):
        tools = result.get("tools")
        if isinstance(tools, list):
            return tools
    return []


def _result_content_text(payload: dict) -> str | None:
    """Extract the first text content block from a tool result payload."""
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
    """Extract the first structured content block from a tool result payload."""
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


def _header_value(payload: dict, header_name: str) -> str | None:
    """Return one response header value using a case-insensitive lookup."""
    headers = payload.get("_headers", {})
    if not isinstance(headers, dict):
        return None
    target = header_name.lower()
    for key, value in headers.items():
        if str(key).lower() == target and isinstance(value, str):
            return value
    return None


def _initialize_has_session_header(payload: dict) -> bool:
    """Return whether a response payload includes ``MCP-Session-Id``."""
    return bool(_header_value(payload, "MCP-Session-Id"))


def _initialize_success_check(payload: dict) -> bool:
    """Return whether an initialize payload represents success."""
    return isinstance(payload.get("result"), dict) and "capabilities" in payload.get("result", {})


def _initialize_failure_without_session_check(payload: dict) -> bool:
    """Return whether a failed initialize omitted session creation."""
    return isinstance(payload.get("error"), dict) and not _initialize_has_session_header(payload)


def _reason_code(payload: dict) -> str | None:
    """Extract the highest-signal reason code from a verification payload."""
    reason = payload.get("reason")
    if isinstance(reason, dict):
        code = reason.get("code")
        if isinstance(code, str):
            return code
    error = payload.get("error")
    if isinstance(error, dict):
        data = error.get("data")
        if isinstance(data, dict):
            category = data.get("category")
            if isinstance(category, str):
                return category
    return None


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
    dependency_checks_enabled = bool(revision.secret_reference_names) or revision.secret_access_mode != "env_only" or (
        revision.session_backend == "redis"
    ) or bool(revision.session_store_url) or bool(revision.session_connectivity_model)

    remediation = {
        "deployment-evidence": "Inspect deployment metadata, runtime identity, secret reference names, and session connectivity fields before re-running verification.",
        "reachability": "Inspect Cloud Run public invocation, the published service URL, and provider-level access settings before re-running verification.",
        "liveness": "Inspect the deployed revision startup logs and confirm the container is listening on the expected port.",
        "secret-access": "Inspect runtime identity bindings, secret references, and secret injection wiring before re-running verification.",
        "readiness": "Review runtime configuration and secret injection, then redeploy or re-run verification.",
        "session-connectivity": "Inspect Cloud Run-to-session-backend connectivity wiring and backend availability before re-running verification.",
        "initialize-invalid-no-session": "Confirm rejected initialize requests return no MCP-Session-Id and do not create usable session state before re-running verification.",
        "initialize-success-session-created": "Confirm successful initialize responses still issue MCP-Session-Id and declare capabilities before re-running verification.",
        "initialize-retry-success": "Confirm a successful initialize after a rejected initialize creates the first usable hosted session before re-running verification.",
        "initialize": "Confirm the hosted MCP endpoint is reachable and the initialize method is still supported.",
        "list-tools": "Confirm the hosted registry remains discoverable before re-running verification.",
        "search-tool-call-openai": "Inspect the published OpenAI-compatible search schema, hosted tool dispatch, and retrieval example inputs before re-running verification.",
        "fetch-tool-call-openai": "Inspect OpenAI-compatible fetch discovery metadata and hosted retrieval handling before re-running verification.",
        "search-tool-call-empty": "Inspect empty-result handling for the OpenAI-compatible search contract before re-running verification.",
        "fetch-tool-call-legacy-shape": "Inspect legacy-shape validation and compatibility-boundary handling before re-running verification.",
        "fetch-tool-call-missing": "Inspect missing-document validation and hosted error mapping before re-running verification.",
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
        "deployment-evidence": "deployment-time",
        "reachability": "deployment-time",
        "liveness": "deployment-time",
        "secret-access": "readiness-time",
        "readiness": "readiness-time",
        "session-connectivity": "readiness-time",
        "initialize-invalid-no-session": "MCP-time",
        "initialize-success-session-created": "MCP-time",
        "initialize-retry-success": "MCP-time",
        "initialize": "MCP-time",
        "list-tools": "MCP-time",
        "search-tool-call-openai": "MCP-time",
        "fetch-tool-call-openai": "MCP-time",
        "search-tool-call-empty": "MCP-time",
        "fetch-tool-call-legacy-shape": "MCP-time",
        "fetch-tool-call-missing": "MCP-time",
        "session-post-continuation": "MCP-time",
        "session-get-continuation": "MCP-time",
        "session-reconnect": "MCP-time",
        "session-invalid": "MCP-time",
        "browser-preflight-approved": "browser-time",
        "browser-request-approved": "browser-time",
        "browser-origin-denied": "browser-time",
        "browser-request-unsupported": "browser-time",
    }

    def _finalize(result: str) -> HostedVerificationRun:
        return HostedVerificationRun(
            revision.revision_name,
            revision.runtime_identity,
            started_at,
            _now_iso(),
            result,
            tuple(checks),
            revision.session_network_reference,
            revision.session_subnet_reference,
            revision.session_connector_reference,
        )

    def _append(check_name: str, payload: dict, expected: Callable[[dict], bool], summary: str) -> bool:
        ok = expected(payload)
        result_summary = summary
        if not ok:
            result_summary = f"{stage[check_name]} failure during {check_name}. {remediation[check_name]}"
        request_reached_application = check_name != "reachability"
        if ok:
            failure_layer = "none"
        elif check_name == "deployment-evidence":
            failure_layer = "secret_access"
            request_reached_application = False
        elif check_name == "reachability":
            failure_layer = "cloud_platform"
            request_reached_application = False
        elif check_name in {"secret-access", "readiness"} and (_reason_code(payload) or "").startswith("SECRET_"):
            failure_layer = "secret_access"
        elif check_name in {"session-connectivity", "readiness"} and (_reason_code(payload) or "").startswith("SESSION_"):
            failure_layer = "session_connectivity"
        elif check_name in {"liveness", "readiness"} and payload.get("statusCode") in {None, 502, 503, 504}:
            failure_layer = "cloud_platform"
            request_reached_application = False
        else:
            failure_layer = "mcp_application"
        checks.append(
            VerificationCheckResult(
                check_name=check_name,
                endpoint_url=revision.endpoint_url,
                executed_at=_now_iso(),
                result="pass" if ok else "fail",
                summary=result_summary,
                status_code=payload.get("statusCode"),
                evidence_location=evidence_path,
                failure_layer=failure_layer,
                request_reached_application=request_reached_application,
                remediation=remediation[check_name] if not ok else None,
            )
        )
        return ok

    if dependency_checks_enabled:
        deployment_payload = {
            "runtimeIdentity": revision.runtime_identity,
            "secretReferenceNames": list(revision.secret_reference_names),
            "secretAccessMode": revision.secret_access_mode,
            "sessionBackend": revision.session_backend,
            "sessionStoreUrl": revision.session_store_url,
            "sessionConnectivityModel": revision.session_connectivity_model,
            "sessionNetworkReference": revision.session_network_reference,
            "sessionSubnetReference": revision.session_subnet_reference,
            "sessionConnectorReference": revision.session_connector_reference,
        }
        deployment_ok = bool(revision.runtime_identity)
        if revision.secret_access_mode == "secret_manager_env":
            deployment_ok = deployment_ok and bool(revision.secret_reference_names)
        if revision.session_backend == "redis":
            deployment_ok = (
                deployment_ok
                and bool(revision.session_store_url)
                and bool(revision.session_connectivity_model)
                and bool(revision.session_network_reference)
                and bool(revision.session_subnet_reference)
                and bool(revision.session_connector_reference)
            )
        if not _append(
            "deployment-evidence",
            deployment_payload,
            lambda _payload: deployment_ok,
            "Deployment metadata included runtime identity, secret access evidence, and session connectivity evidence.",
        ):
            return _finalize("fail")

    reachability_payload = _normalize_request_result(requester("/", {"__httpMethod": "GET"}))
    if not _append(
        "reachability",
        reachability_payload,
        lambda payload: payload.get("statusCode") is not None and payload.get("statusCode") not in {401, 403},
        "Hosted connection point responded to an unauthenticated reachability probe.",
    ):
        return _finalize("fail")

    health_payload = _normalize_request_result(requester("/health", {"__httpMethod": "GET"}))
    if not _append(
        "liveness",
        health_payload,
        lambda payload: payload.get("status") == "ok",
        "Hosted liveness endpoint returned healthy status.",
    ):
        return _finalize("fail")

    ready_payload = _normalize_request_result(requester("/ready", {"__httpMethod": "GET"}))
    if dependency_checks_enabled:
        if not _append(
            "secret-access",
            ready_payload,
            lambda payload: payload.get("checks", {}).get("secrets") == "pass",
            "Hosted readiness reported healthy secret access state.",
        ):
            return _finalize("fail")
    if not _append(
        "readiness",
        ready_payload,
        lambda payload: payload.get("status") == "ready",
        "Hosted readiness endpoint returned ready status.",
    ):
        return _finalize("fail")
    if dependency_checks_enabled:
        if not _append(
            "session-connectivity",
            ready_payload,
            lambda payload: payload.get("checks", {}).get("sessionDurability") == "pass",
            "Hosted readiness reported healthy session connectivity state.",
        ):
            return _finalize("fail")

    invalid_initialize_payload = _normalize_request_result(
        requester(
        "/mcp",
        {
            "jsonrpc": "2.0",
            "id": "verify-init-invalid",
            "method": "initialize",
            "params": {},
        },
        )
    )
    if not _append(
        "initialize-invalid-no-session",
        invalid_initialize_payload,
        lambda payload: payload.get("statusCode") == 400 and _initialize_failure_without_session_check(payload),
        "Rejected initialize returned no session header and no successful initialize result.",
    ):
        return _finalize("fail")

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
        "initialize-success-session-created",
        initialize_payload,
        lambda payload: payload.get("statusCode") == 200 and _initialize_success_check(payload) and _initialize_has_session_header(payload),
        "Successful initialize returned declared capabilities and issued MCP-Session-Id.",
    ):
        return _finalize("fail")
    if not _append(
        "initialize-retry-success",
        initialize_payload,
        lambda payload: payload.get("statusCode") == 200 and _initialize_success_check(payload) and _initialize_has_session_header(payload),
        "A successful initialize after a rejected initialize created the first usable hosted session.",
    ):
        return _finalize("fail")
    if not _append(
        "initialize",
        initialize_payload,
        _initialize_success_check,
        "Hosted MCP initialize returned declared capabilities.",
    ):
        return _finalize("fail")

    list_payload = _normalize_request_result(
        requester("/mcp", {"jsonrpc": "2.0", "id": "verify-list", "method": "tools/list", "params": {}})
    )
    if not _append(
        "list-tools",
        list_payload,
        lambda payload: {"search", "fetch"}.issubset({tool.get("name") for tool in _result_tools(payload)}),
        "Hosted MCP tool discovery returned the deep research tool set.",
    ):
        return _finalize("fail")

    search_payload = _normalize_request_result(
        requester(
            "/mcp",
            {
                "jsonrpc": "2.0",
                "id": "verify-search-tool-call",
                "method": "tools/call",
                "params": {"name": "search", "arguments": {"query": "remote MCP research"}},
            },
        )
    )
    if not _append(
        "search-tool-call-openai",
        search_payload,
        lambda payload: isinstance(_result_structured_content(payload), dict)
        and len(_result_structured_content(payload).get("results", [])) >= 1
        and isinstance(_result_structured_content(payload).get("results", [])[0], dict)
        and {"id", "title", "url"}.issubset(_result_structured_content(payload).get("results", [])[0].keys()),
        "Hosted MCP search call succeeded using the OpenAI-compatible request input.",
    ):
        return _finalize("fail")

    search_structured = _result_structured_content(search_payload) or {}
    search_results = search_structured.get("results", []) if isinstance(search_structured, dict) else []
    first_result = search_results[0] if search_results else {}
    document_id = first_result.get("id", "doc-remote-mcp-001")

    fetch_payload = _normalize_request_result(
        requester(
            "/mcp",
            {
                "jsonrpc": "2.0",
                "id": "verify-fetch-openai",
                "method": "tools/call",
                "params": {"name": "fetch", "arguments": {"id": document_id}},
            },
        )
    )
    if not _append(
        "fetch-tool-call-openai",
        fetch_payload,
        lambda payload: isinstance(_result_structured_content(payload), dict)
        and _result_structured_content(payload).get("id") == document_id,
        "Hosted MCP fetch call succeeded using the discovery-derived OpenAI-compatible id pattern.",
    ):
        return _finalize("fail")

    empty_search_payload = _normalize_request_result(
        requester(
            "/mcp",
            {
                "jsonrpc": "2.0",
                "id": "verify-search-empty",
                "method": "tools/call",
                "params": {"name": "search", "arguments": {"query": "no-match-sentinel"}},
            },
        )
    )
    if not _append(
        "search-tool-call-empty",
        empty_search_payload,
        lambda payload: isinstance(_result_structured_content(payload), dict)
        and _result_structured_content(payload).get("results") == [],
        "Hosted MCP search call returned the documented empty-results success shape.",
    ):
        return _finalize("fail")

    legacy_fetch_payload = _normalize_request_result(
        requester(
            "/mcp",
            {
                "jsonrpc": "2.0",
                "id": "verify-fetch-legacy-shape",
                "method": "tools/call",
                "params": {"name": "fetch", "arguments": {"resourceId": "res_remote_mcp_001"}},
            },
        )
    )
    if not _append(
        "fetch-tool-call-legacy-shape",
        legacy_fetch_payload,
        lambda payload: payload.get("error", {}).get("code") == -32602
        and payload.get("error", {}).get("data", {}).get("category") == "invalid_argument",
        "Hosted MCP fetch call using a legacy request shape returned the documented invalid-input failure.",
    ):
        return _finalize("fail")

    missing_fetch_payload = _normalize_request_result(
        requester(
            "/mcp",
            {
                "jsonrpc": "2.0",
                "id": "verify-fetch-missing",
                "method": "tools/call",
                "params": {"name": "fetch", "arguments": {"id": "missing-resource"}},
            },
        )
    )
    _append(
        "fetch-tool-call-missing",
        missing_fetch_payload,
        lambda payload: payload.get("error", {}).get("code") == -32001
        and payload.get("error", {}).get("data", {}).get("category") == "unavailable_source",
        "Hosted MCP fetch call for an unavailable document returned the documented unavailable-source failure.",
    )

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
        return _finalize("fail")

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
        return _finalize("fail")

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
        return _finalize("fail")

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
        lambda payload: payload.get("statusCode") == 404
        and payload.get("error", {}).get("code") == -32001
        and payload.get("error", {}).get("data", {}).get("category") == "session_not_found",
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
            and _header_value(payload, "Access-Control-Allow-Origin") == browser_origin,
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
            and _header_value(payload, "Access-Control-Allow-Origin") == browser_origin
            and "MCP-Session-Id" in (_header_value(payload, "Access-Control-Expose-Headers") or ""),
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
            lambda payload: payload.get("statusCode") == 403
            and payload.get("error", {}).get("code") == -32003
            and payload.get("error", {}).get("data", {}).get("category") == "origin_denied",
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
            and payload.get("error", {}).get("code") == -32601
            and payload.get("error", {}).get("data", {}).get("category") == "unsupported_browser_route",
            "Unsupported browser request pattern returned the documented denial.",
        )
    overall = "pass" if all(item.result == "pass" for item in checks) else "fail"
    return _finalize(overall)


def write_verification_evidence(destination: str | Path, run: HostedVerificationRun) -> Path:
    """Write a text evidence artifact for a hosted verification run."""
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = serialize_verification_run(run)
    lines = [
        f"revisionName: {payload['revisionName']}",
        f"runtimeIdentity: {payload['runtimeIdentity']}",
        f"startedAt: {payload['startedAt']}",
        f"completedAt: {payload['completedAt']}",
        f"overallResult: {payload['overallResult']}",
        f"sessionNetworkReference: {payload['sessionNetworkReference']}",
        f"sessionSubnetReference: {payload['sessionSubnetReference']}",
        f"sessionConnectorReference: {payload['sessionConnectorReference']}",
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
                f"    failureLayer: {check['failureLayer']}",
                f"    requestReachedApplication: {check['requestReachedApplication']}",
                f"    remediation: {check['remediation']}",
            ]
        )
    path.write_text("\n".join(lines) + "\n")
    return path
