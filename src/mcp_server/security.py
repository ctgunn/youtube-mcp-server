"""Hosted MCP security policy evaluation helpers."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Mapping
from urllib.parse import urlparse


@dataclass(frozen=True)
class HostedSecuritySettings:
    auth_required: bool
    auth_token: str | None
    allowed_origins: tuple[str, ...]
    allow_originless_clients: bool


@dataclass(frozen=True)
class OriginEvaluation:
    client_type: str
    origin_present: bool
    origin_value: str | None
    match_result: str
    reason_code: str


@dataclass(frozen=True)
class CredentialEvaluation:
    scheme: str | None
    present: bool
    token_state: str
    environment_scope: str | None
    safe_fingerprint: str | None = None


@dataclass(frozen=True)
class SecurityDecision:
    request_id: str
    path: str
    decision: str
    decision_category: str
    status_code: int
    client_type: str
    tool_execution_allowed: bool
    origin_present: bool
    auth_present: bool
    origin_reason: str
    credential_state: str


def normalize_origin(value: str | None) -> str | None:
    text = str(value or "").strip()
    if not text:
        return None
    parsed = urlparse(text)
    if not parsed.scheme or not parsed.netloc:
        return None
    return f"{parsed.scheme.lower()}://{parsed.netloc.lower()}"


def parse_allowed_origins(raw: str | None) -> tuple[str, ...]:
    items: list[str] = []
    for entry in str(raw or "").split(","):
        normalized = normalize_origin(entry)
        if normalized:
            items.append(normalized)
    return tuple(dict.fromkeys(items))


def parse_bearer_token(authorization: str | None) -> tuple[str | None, str | None, str]:
    text = str(authorization or "").strip()
    if not text:
        return None, None, "missing"
    scheme, _, token = text.partition(" ")
    if scheme.lower() != "bearer":
        return scheme or None, None, "malformed"
    cleaned = token.strip()
    if not cleaned:
        return "bearer", None, "malformed"
    return "bearer", cleaned, "present"


def evaluate_origin(request_headers: Mapping[str, str], settings: HostedSecuritySettings) -> OriginEvaluation:
    normalized_origin = normalize_origin(request_headers.get("origin"))
    if request_headers.get("origin") and normalized_origin is None:
        return OriginEvaluation(
            client_type="browser",
            origin_present=True,
            origin_value=None,
            match_result="denied",
            reason_code="malformed_origin",
        )
    if normalized_origin is None:
        return OriginEvaluation(
            client_type="non_browser",
            origin_present=False,
            origin_value=None,
            match_result="exempt" if settings.allow_originless_clients else "denied",
            reason_code="originless_client_allowed" if settings.allow_originless_clients else "origin_required",
        )
    return OriginEvaluation(
        client_type="browser",
        origin_present=True,
        origin_value=normalized_origin,
        match_result="allowed" if normalized_origin in settings.allowed_origins else "denied",
        reason_code="origin_allowed" if normalized_origin in settings.allowed_origins else "origin_not_allowed",
    )


def _fingerprint(token: str | None) -> str | None:
    if not token:
        return None
    return hashlib.sha256(token.encode("utf-8")).hexdigest()[:12]


def evaluate_credential(
    request_headers: Mapping[str, str],
    settings: HostedSecuritySettings,
    *,
    environment: str,
) -> CredentialEvaluation:
    scheme, token, state = parse_bearer_token(request_headers.get("authorization"))
    if not settings.auth_required:
        return CredentialEvaluation(
            scheme=scheme,
            present=state != "missing",
            token_state="valid",
            environment_scope=environment,
            safe_fingerprint=_fingerprint(token),
        )
    if state == "missing":
        return CredentialEvaluation(scheme=None, present=False, token_state="missing", environment_scope=environment)
    if state == "malformed":
        return CredentialEvaluation(scheme=scheme, present=True, token_state="malformed", environment_scope=environment)
    if settings.auth_token is None:
        return CredentialEvaluation(
            scheme="bearer",
            present=True,
            token_state="environment_mismatch",
            environment_scope=environment,
            safe_fingerprint=_fingerprint(token),
        )
    if token != settings.auth_token:
        return CredentialEvaluation(
            scheme="bearer",
            present=True,
            token_state="invalid",
            environment_scope=environment,
            safe_fingerprint=_fingerprint(token),
        )
    return CredentialEvaluation(
        scheme="bearer",
        present=True,
        token_state="valid",
        environment_scope=environment,
        safe_fingerprint=_fingerprint(token),
    )


def evaluate_security_request(
    request_headers: Mapping[str, str],
    settings: HostedSecuritySettings,
    *,
    path: str,
    request_id: str,
    environment: str,
) -> SecurityDecision:
    origin = evaluate_origin(request_headers, settings)
    if origin.match_result == "denied":
        malformed = origin.reason_code == "malformed_origin"
        return SecurityDecision(
            request_id=request_id,
            path=path,
            decision="denied",
            decision_category="malformed_security_input" if malformed else "origin_denied",
            status_code=400 if malformed else 403,
            client_type=origin.client_type,
            tool_execution_allowed=False,
            origin_present=origin.origin_present,
            auth_present=bool(request_headers.get("authorization")),
            origin_reason=origin.reason_code,
            credential_state="not_evaluated",
        )

    credential = evaluate_credential(request_headers, settings, environment=environment)
    if credential.token_state != "valid":
        category = {
            "missing": "unauthenticated",
            "malformed": "malformed_security_input",
            "invalid": "invalid_credential",
            "environment_mismatch": "invalid_credential",
            "expired": "invalid_credential",
        }.get(credential.token_state, "invalid_credential")
        status_code = 401 if credential.token_state == "missing" else 400 if credential.token_state == "malformed" else 403
        return SecurityDecision(
            request_id=request_id,
            path=path,
            decision="denied",
            decision_category=category,
            status_code=status_code,
            client_type=origin.client_type,
            tool_execution_allowed=False,
            origin_present=origin.origin_present,
            auth_present=credential.present,
            origin_reason=origin.reason_code,
            credential_state=credential.token_state,
        )

    return SecurityDecision(
        request_id=request_id,
        path=path,
        decision="accepted",
        decision_category="accepted",
        status_code=200,
        client_type=origin.client_type,
        tool_execution_allowed=True,
        origin_present=origin.origin_present,
        auth_present=credential.present,
        origin_reason=origin.reason_code,
        credential_state=credential.token_state,
    )
