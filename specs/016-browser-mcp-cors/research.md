# Research: FND-016 Browser-Originated MCP Access + CORS Support

## Decision 1: Restrict explicit browser access to hosted MCP routes that are already intentionally exposed

Rationale:
- The current hosted surface already distinguishes `/mcp`, `/health`, and `/ready`, with security controls concentrated around `/mcp`.
- FND-016 is about making browser-facing behavior explicit, not broadening the service surface.
- Keeping browser behavior scoped to documented hosted routes preserves simplicity and avoids accidentally treating unsupported paths as browser-enabled.

Alternatives considered:
- Enable browser CORS behavior for every hosted route by default.
  - Rejected because it would expand browser reach beyond the feature scope and weaken the “explicit support only” requirement.
- Only support browser behavior for `POST /mcp` and ignore any preflightable variants.
  - Rejected because browsers need deliberate preflight and response behavior for the documented request patterns, not only the terminal request.

## Decision 2: Treat browser preflight as a first-class hosted interaction with stable route and method rules

Rationale:
- The current hosted route classifier only recognizes `GET` and `POST`; browsers need explicit `OPTIONS` handling to avoid implicit failures.
- Stable preflight behavior is required so approved clients can distinguish “supported browser request” from “unsupported browser request” before sending credentials and MCP payloads.
- First-class preflight handling keeps browser support observable and testable at the transport boundary.

Alternatives considered:
- Rely on generic framework defaults for `OPTIONS`.
  - Rejected because the current hosted entrypoint owns the transport contract and browser behavior must be deliberate, not incidental.
- Answer every `OPTIONS` request with a blanket success.
  - Rejected because it would hide route, method, and origin restrictions instead of expressing them.

## Decision 3: Preserve the existing authentication and origin policy as the source of truth for browser approval

Rationale:
- FND-013 already introduced an origin-aware security boundary and documented auth strategy.
- Browser-origin support should extend that policy with explicit headers and preflight semantics, not create a parallel access-control system.
- Reusing the current origin allowlist and auth expectations keeps browser and non-browser access consistent and reduces policy drift.

Alternatives considered:
- Add a separate browser-only allowlist unrelated to `MCP_ALLOWED_ORIGINS`.
  - Rejected because it would create two competing approval models for the same hosted surface.
- Allow approved origins to bypass authentication after a successful preflight.
  - Rejected because preflight is not an authorization mechanism and that would weaken the current hosted security model.

## Decision 4: Apply response headers only when the origin and route qualify for documented browser support

Rationale:
- Approved browser requests need explicit allow headers on both preflight and actual responses.
- Denied or unsupported browser requests should not look like successful grants.
- Conditional response headers make the support decision visible without leaking browser access to requests that fall outside the contract.

Alternatives considered:
- Emit browser allow headers on every hosted MCP response.
  - Rejected because it would blur the distinction between approved and denied browser access.
- Only emit headers on preflight responses.
  - Rejected because browsers also need the documented cross-origin headers on actual responses.

## Decision 5: Keep originless clients on the existing non-browser path

Rationale:
- The current hosted security model already allows originless clients when configured to do so, and many MCP consumers are not browsers.
- FND-016 adds browser support; it does not convert all hosted consumers into browser clients.
- Preserving the non-browser path avoids a regression in existing remote MCP consumers while keeping browser rules isolated to requests that actually present an origin.

Alternatives considered:
- Require every hosted client to send an origin once browser support exists.
  - Rejected because it would break legitimate non-browser clients and expand scope beyond browser-originated access.
- Treat missing origin as a denied browser request.
  - Rejected because it conflicts with the existing explicit originless-client setting and would regress supported clients.

## Decision 6: Use stable denial categories for disallowed origins and unsupported browser request patterns

Rationale:
- Operators and integrators need to tell apart “origin denied,” “unsupported browser pattern,” “authentication failed,” and “session or protocol failed.”
- Stable denial outcomes align with the existing structured error model and keep browser failures diagnosable.
- This supports both the feature spec and the constitution’s observability requirement.

Alternatives considered:
- Return one generic browser failure for every rejected browser request.
  - Rejected because it would hide the difference between policy denial and malformed or unsupported use.
- Fall through to existing generic method or path errors without browser-specific shaping.
  - Rejected because it would keep browser behavior implicit and harder to document.

## Decision 7: Extend hosted verification to cover approved and denied browser scenarios explicitly

Rationale:
- Browser CORS regressions are easy to miss if tests only exercise server-to-server request flows.
- The repository already has hosted verification and security-focused contract/integration suites that can absorb browser-specific scenarios.
- Adding explicit verification for approved preflight, approved response headers, denied origin, and unsupported browser patterns gives operators release evidence instead of assumptions.

Alternatives considered:
- Rely only on unit tests for header generation.
  - Rejected because browser support is a contract at the hosted transport boundary.
- Defer browser verification to manual testing after implementation.
  - Rejected because the constitution requires integration and regression coverage rather than manual-only assurance.

## Decision 8: Keep the implementation centered in the hosted entrypoint and transport/security helpers

Rationale:
- Browser-origin support is a hosted transport concern layered above MCP method handling.
- The current architecture already routes hosted request classification, security decisions, and response shaping through `cloud_run_entrypoint.py`, `transport/http.py`, and `security.py`.
- Constraining implementation to those seams minimizes churn and reduces the chance of introducing protocol regressions deeper in the MCP core.

Alternatives considered:
- Push browser handling into tool dispatch or protocol method handlers.
  - Rejected because browser CORS behavior belongs at the HTTP boundary, not in tool logic.
- Introduce a separate browser-only service tier.
  - Rejected because it would add unnecessary complexity for a transport-surface feature.
