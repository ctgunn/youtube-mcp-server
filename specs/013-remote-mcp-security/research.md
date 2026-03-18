# Research: Remote MCP Security and Transport Hardening

## Decision 1: Require bearer-token authentication for hosted MCP access

- **Decision**: Use a single operator-managed bearer token as the required remote authentication mechanism for hosted `/mcp` access, with enforcement mandatory in `staging` and `prod` and explicitly configurable for local `dev` verification.
- **Rationale**: The current hosted runtime has no remote auth layer, and FND-013 needs a concrete, implementable security boundary before external MCP clients can be supported safely. A single bearer token fits the existing secret-backed configuration model, works for third-party MCP clients, and can be enforced at the transport boundary without introducing user-account workflows.
- **Alternatives considered**:
  - OAuth client flows: stronger long-term option but out of scope for this foundational hardening slice and introduces account-management complexity not required by the spec.
  - IAP- or proxy-only protection: useful in some deployments but insufficient as the only documented client contract because the application still needs stable auth semantics for direct hosted MCP consumption.
  - No auth in `dev`, `staging`, and `prod`: rejected because it would leave the hosted MCP surface inconsistent with the PRD security requirements.

## Decision 2: Apply origin-aware checks only when an `Origin` header is present, with explicit allowlist matching for browser callers

- **Decision**: Treat requests with an `Origin` header as browser-originated and require an exact match against a configured allowlist; treat requests without `Origin` as non-browser clients and allow them to proceed to authentication checks instead of rejecting them outright.
- **Rationale**: Modern remote MCP clients may run server-to-server and omit `Origin`, while browser-based consumers must be constrained by an allowlist to avoid unsafe cross-origin access. This model aligns with the feature spec, preserves valid non-browser integrations, and improves on the current same-host/localhost heuristic.
- **Alternatives considered**:
  - Require `Origin` for every request: rejected because it would break legitimate non-browser MCP clients.
  - Accept any `Origin` when auth is valid: rejected because browser trust and credential possession are separate controls.
  - Continue same-host-or-localhost detection only: rejected because it is too implicit for hosted third-party consumption and not operator-configurable.

## Decision 3: Use a stable security failure taxonomy with transport-level denial before MCP execution

- **Decision**: Return stable denial behavior with distinct categories for missing/invalid credentials, disallowed origin, malformed security headers, and unsupported hosted request patterns; evaluate these checks before MCP tool execution or session mutation.
- **Rationale**: The feature requires predictable client behavior and operator diagnosis. Distinct denial categories let clients correct requests and let tests prove that unsafe requests are rejected before reaching protected MCP flows.
- **Alternatives considered**:
  - Reuse one generic forbidden error for all security failures: rejected because it weakens diagnosis and documentation quality.
  - Delay auth/origin checks until after MCP request parsing or session handling: rejected because it increases exposure and complicates reasoning about protected flows.

## Decision 4: Record security decisions in structured observability without logging secrets

- **Decision**: Emit structured security decision records that include request identifier, hosted path, decision category, caller classification, and whether origin/auth data was present, while never logging raw credentials or secret values.
- **Rationale**: The constitution requires observability and security together. Operators need enough context to trace denials, but logs must remain safe for Cloud Logging and incident review.
- **Alternatives considered**:
  - Log full request headers for convenience: rejected because it risks credential leakage.
  - Log only aggregate denial counts: rejected because it would not support per-request investigation.

## Decision 5: Treat security configuration as startup-validated hosted runtime input

- **Decision**: Add hosted security settings to the runtime configuration contract and fail readiness clearly when mandatory production security settings are missing or invalid.
- **Rationale**: FND-013 changes the hosted entry contract, so operators need predictable deployment-time validation instead of discovering misconfiguration only through rejected client traffic.
- **Alternatives considered**:
  - Lazy validation on first secured request: rejected because it delays failure discovery and weakens deployment confidence.
  - Hard-code policies in source without runtime configuration: rejected because it blocks environment-specific control and documentation clarity.

## Decision 6: Update hosted verification and documentation to include both success and denial paths

- **Decision**: Extend local and hosted verification guidance to cover one successful authenticated MCP interaction plus representative missing-auth and disallowed-origin denials.
- **Rationale**: This feature changes the external contract, so documentation must prove both supported and rejected behaviors. That also satisfies the constitution requirement for contract-first planning and regression-friendly verification.
- **Alternatives considered**:
  - Document only the successful path: rejected because it leaves failure handling ambiguous for integrators.
  - Rely on tests without updating operator guidance: rejected because hosted rollout and support depend on documented usage.
