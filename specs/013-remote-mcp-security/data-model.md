# Data Model: Remote MCP Security and Transport Hardening

## HostedSecurityConfiguration

- **Purpose**: Defines the operator-managed security settings that determine whether hosted MCP requests are admitted.
- **Fields**:
  - `environment`: runtime profile (`dev`, `staging`, `prod`)
  - `auth_required`: whether hosted `/mcp` requests must present credentials
  - `auth_token_reference`: secret-backed source for the expected bearer token
  - `allowed_origins`: exact-match list of browser origins permitted for hosted access
  - `allow_originless_clients`: whether non-browser callers without `Origin` may proceed to auth checks
  - `deny_by_default`: whether unknown origins are rejected automatically
  - `checked_at`: timestamp of the latest configuration validation
- **Validation rules**:
  - `environment` must match a supported runtime profile.
  - `auth_token_reference` is required when `auth_required` is true.
  - `allowed_origins` must contain normalized absolute origins when browser access is supported.
  - `allow_originless_clients` cannot bypass authentication when `auth_required` is true.
- **Relationships**:
  - Feeds `OriginTrustRule` evaluation.
  - Feeds `SecurityDecisionRecord` outcomes.

## OriginTrustRule

- **Purpose**: Represents the effective rule used to classify browser and non-browser hosted callers.
- **Fields**:
  - `client_type`: `browser` or `non_browser`
  - `origin_present`: whether the request included an `Origin` header
  - `origin_value`: normalized origin value when present
  - `match_result`: `allowed`, `denied`, or `exempt`
  - `reason_code`: stable explanation for the decision
- **Validation rules**:
  - `origin_value` must be absent when `origin_present` is false.
  - `match_result=allowed` requires either allowlist match or documented exemption for originless non-browser clients.
  - `reason_code` must map to a client-visible denial category when `match_result=denied`.
- **Relationships**:
  - Produced from `HostedSecurityConfiguration`.
  - Combined with `RemoteAccessCredential` to create a `SecurityDecisionRecord`.

## RemoteAccessCredential

- **Purpose**: Represents the caller-provided credential used to access hosted MCP flows.
- **Fields**:
  - `scheme`: expected credential scheme for hosted access
  - `present`: whether a credential was supplied
  - `token_state`: `valid`, `missing`, `invalid`, `expired`, or `environment_mismatch`
  - `environment_scope`: runtime environment the credential is valid for
  - `safe_fingerprint`: optional non-secret identifier for operator diagnostics
- **Validation rules**:
  - `scheme` must match the documented hosted access contract.
  - `token_state=valid` requires `present=true`.
  - Raw credential material must never be stored in logs or returned in responses.
- **Relationships**:
  - Evaluated after origin handling and before protected MCP processing.
  - Contributes to `SecurityDecisionRecord`.

## SecurityDecisionRecord

- **Purpose**: Captures the auditable outcome of hosted request security evaluation.
- **Fields**:
  - `request_id`: correlation identifier for the request
  - `path`: hosted route under evaluation
  - `decision`: `accepted` or `denied`
  - `decision_category`: `origin_denied`, `unauthenticated`, `invalid_credential`, `malformed_security_input`, `unsupported_request`, or `accepted`
  - `client_type`: browser or non-browser
  - `tool_execution_allowed`: whether MCP handling may continue
  - `status_code`: transport-level status returned to the caller
  - `logged_at`: timestamp for the decision
- **Validation rules**:
  - `tool_execution_allowed` must be false for every denied decision.
  - `status_code` must align to the documented hosted contract for the decision category.
  - `decision_category=accepted` requires `decision=accepted`.
- **Relationships**:
  - Summarizes `OriginTrustRule` and `RemoteAccessCredential` evaluation.
  - Emitted through observability.

## State Transitions

### Hosted Request Security Evaluation

1. `received` -> request metadata normalized.
2. `origin_evaluated` -> browser-originated request matched against allowlist or originless caller marked exempt/denied.
3. `credential_evaluated` -> credential classified as valid or denied.
4. `accepted` -> request may continue into MCP session and tool handling.
5. `denied` -> request returns a stable security failure before protected processing.

### Configuration Readiness

1. `config_loaded` -> runtime security inputs discovered.
2. `config_validated` -> required security settings confirmed for environment.
3. `ready` -> hosted service may accept protected MCP requests.
4. `degraded` -> missing or invalid security settings prevent ready state for protected hosted use.
