"""Hosted MCP security policy evaluation helpers."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Mapping
from urllib.parse import urlparse

DEFAULT_BROWSER_ACCESSIBLE_ROUTES = ("/mcp",)
DEFAULT_BROWSER_ALLOWED_METHODS = ("GET", "POST")
DEFAULT_BROWSER_ALLOWED_REQUEST_HEADERS = (
    "authorization",
    "content-type",
    "mcp-session-id",
    "last-event-id",
    "mcp-protocol-version",
)
DEFAULT_BROWSER_EXPOSED_RESPONSE_HEADERS = (
    "MCP-Session-Id",
    "MCP-Protocol-Version",
    "X-Stream-Id",
)

MCP_APPLICATION_SECURITY_CATEGORIES = (
    "unauthenticated",
    "invalid_credential",
    "origin_denied",
    "malformed_security_input",
)


@dataclass(frozen=True)
class HostedSecuritySettings:
    auth_required: bool
    auth_token: str | None
    allowed_origins: tuple[str, ...]
    allow_originless_clients: bool
    browser_accessible_routes: tuple[str, ...] = DEFAULT_BROWSER_ACCESSIBLE_ROUTES
    browser_allowed_methods: tuple[str, ...] = DEFAULT_BROWSER_ALLOWED_METHODS
    browser_allowed_request_headers: tuple[str, ...] = DEFAULT_BROWSER_ALLOWED_REQUEST_HEADERS
    browser_exposed_response_headers: tuple[str, ...] = DEFAULT_BROWSER_EXPOSED_RESPONSE_HEADERS
    browser_preflight_max_age_seconds: int = 600


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


@dataclass(frozen=True)
class BrowserPreflightEvaluation:
    decision_category: str
    status_code: int
    origin_value: str | None
    requested_method: str | None
    requested_headers: tuple[str, ...]


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


def parse_requested_headers(raw: str | None) -> tuple[str, ...]:
    headers: list[str] = []
    for entry in str(raw or "").split(","):
        cleaned = entry.strip().lower()
        if cleaned:
            headers.append(cleaned)
    return tuple(dict.fromkeys(headers))


def evaluate_browser_preflight(
    *,
    path: str,
    request_headers: Mapping[str, str],
    settings: HostedSecuritySettings,
) -> BrowserPreflightEvaluation:
    origin = evaluate_origin(request_headers, settings)
    if origin.match_result == "denied":
        return BrowserPreflightEvaluation(
            decision_category=origin.reason_code if origin.reason_code == "malformed_origin" else "origin_denied",
            status_code=400 if origin.reason_code == "malformed_origin" else 403,
            origin_value=origin.origin_value,
            requested_method=None,
            requested_headers=(),
        )

    if not origin.origin_present:
        return BrowserPreflightEvaluation(
            decision_category="malformed_security_input",
            status_code=400,
            origin_value=None,
            requested_method=None,
            requested_headers=(),
        )

    if path not in settings.browser_accessible_routes:
        return BrowserPreflightEvaluation(
            decision_category="unsupported_browser_route",
            status_code=405,
            origin_value=origin.origin_value,
            requested_method=None,
            requested_headers=(),
        )

    requested_method = str(request_headers.get("access-control-request-method") or "").strip().upper()
    if not requested_method:
        return BrowserPreflightEvaluation(
            decision_category="malformed_security_input",
            status_code=400,
            origin_value=origin.origin_value,
            requested_method=None,
            requested_headers=(),
        )
    if requested_method not in settings.browser_allowed_methods:
        return BrowserPreflightEvaluation(
            decision_category="unsupported_browser_method",
            status_code=405,
            origin_value=origin.origin_value,
            requested_method=requested_method,
            requested_headers=(),
        )

    requested_headers = parse_requested_headers(request_headers.get("access-control-request-headers"))
    unsupported_headers = [header for header in requested_headers if header not in settings.browser_allowed_request_headers]
    if unsupported_headers:
        return BrowserPreflightEvaluation(
            decision_category="unsupported_browser_headers",
            status_code=400,
            origin_value=origin.origin_value,
            requested_method=requested_method,
            requested_headers=requested_headers,
        )

    return BrowserPreflightEvaluation(
        decision_category="approved",
        status_code=204,
        origin_value=origin.origin_value,
        requested_method=requested_method,
        requested_headers=requested_headers,
    )


def browser_preflight_headers(
    evaluation: BrowserPreflightEvaluation,
    settings: HostedSecuritySettings,
) -> dict[str, str]:
    if evaluation.decision_category != "approved" or evaluation.origin_value is None:
        return {}
    allow_headers = evaluation.requested_headers or settings.browser_allowed_request_headers
    return {
        "Access-Control-Allow-Origin": evaluation.origin_value,
        "Access-Control-Allow-Methods": ", ".join(settings.browser_allowed_methods),
        "Access-Control-Allow-Headers": ", ".join(allow_headers),
        "Access-Control-Max-Age": str(settings.browser_preflight_max_age_seconds),
        "Vary": "Origin, Access-Control-Request-Method, Access-Control-Request-Headers",
    }


def browser_response_headers(
    *,
    path: str,
    request_headers: Mapping[str, str],
    settings: HostedSecuritySettings,
) -> dict[str, str]:
    origin = evaluate_origin(request_headers, settings)
    if (
        not origin.origin_present
        or origin.match_result != "allowed"
        or path not in settings.browser_accessible_routes
    ):
        return {}
    return {
        "Access-Control-Allow-Origin": origin.origin_value or "",
        "Access-Control-Expose-Headers": ", ".join(settings.browser_exposed_response_headers),
        "Vary": "Origin",
    }


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


def is_mcp_application_security_category(value: str) -> bool:
    return str(value or "").strip() in MCP_APPLICATION_SECURITY_CATEGORIES
