# Research: FND-018 JSON-RPC / MCP Error Code Alignment

## Decision 1: Use numeric JSON-RPC-style codes for all covered client-visible MCP error responses

Rationale:
- FND-018 exists because the current `error.code` field is still a server-specific string taxonomy even after the response envelope became MCP-native in FND-010.
- Numeric codes align the service with the expected JSON-RPC / MCP convention for `error.code` while preserving the existing `jsonrpc`, `message`, and `data` structure.
- A numeric contract lets downstream clients classify failures without first normalizing string enums such as `INVALID_ARGUMENT`, `METHOD_NOT_SUPPORTED`, or `ORIGIN_DENIED`.

Alternatives considered:
- Keep string codes and only document them better.
  - Rejected because it does not address the core interoperability gap called out by FND-018.
- Introduce both numeric and string top-level codes in parallel.
  - Rejected because dual typing would keep the client contract ambiguous and prolong migration complexity.

## Decision 2: Map core protocol failures to the standard JSON-RPC categories and place service-specific nuance in `error.data.category`

Rationale:
- The strongest protocol-aligned categories already implied by the feature spec are malformed request, unsupported method, invalid argument, and unexpected internal failure.
- Core JSON-RPC-style categories are sufficient for those broad failure classes, while `error.data.category` can preserve the more actionable local meaning needed by operators and higher-level tests.
- This approach keeps the code field stable and compact while avoiding loss of detail for cases such as `expired_session`, `origin_denied`, or `unknown_tool`.

Alternatives considered:
- Encode every fine-grained failure as its own top-level numeric code.
  - Rejected because it would recreate the current over-specific taxonomy in numeric form.
- Remove category details and rely on message text alone.
  - Rejected because category-level detail is still needed for stable tests, rollout diagnostics, and hosted verification evidence.

## Decision 3: Use one reserved negative server-error range for covered failures that are not represented cleanly by the core JSON-RPC categories

Rationale:
- Authentication or authorization denial and explicit resource-lookup failures remain important client-visible distinctions, but they are not a natural fit for only the four common protocol categories.
- A small reserved negative extension range keeps the contract numeric and protocol-safe while avoiding distortion of security and resource failures into unrelated core categories.
- The project already distinguishes these failures operationally through HTTP statuses and detail categories, so a narrow extension range preserves that value without forcing clients back to string parsing.

Alternatives considered:
- Collapse authentication, authorization, and resource-missing cases into `invalid params` or `internal error`.
  - Rejected because it would make client recovery and operator diagnosis materially worse.
- Keep string codes only for security and resource failures while using numeric codes for protocol failures.
  - Rejected because mixed code types are the exact ambiguity this feature is meant to eliminate.

## Decision 4: Preserve current HTTP status behavior and hosted access-control decisions; change only the MCP error-code contract for covered hosted responses

Rationale:
- FND-013 and FND-016 already defined the hosted security and browser-access behavior, including observable status-family expectations for denied requests.
- FND-018 is about error-code alignment, not redefining which requests are allowed or which HTTP status family they should produce.
- Holding HTTP status behavior steady constrains the blast radius and makes it easier to prove that only the code contract changed.

Alternatives considered:
- Redesign both HTTP statuses and MCP error codes together.
  - Rejected because it broadens scope beyond FND-018 and would make regressions much harder to isolate.
- Limit FND-018 to local MCP routing only.
  - Rejected because the spec explicitly requires hosted and local parity for equivalent failures.

## Decision 5: Define explicit precedence rules so each failing request maps to exactly one client-visible code category

Rationale:
- Some requests can appear to fail in more than one way, such as a protected hosted request that is both malformed and unauthorized or a tool call that is structurally valid but references a missing tool.
- Without precedence rules, local and hosted paths will continue to drift because different layers can reject the same request first.
- Precedence keeps the shared mapper deterministic and makes the contract testable across the protocol router, hosted entrypoint, and tool-dispatch layers.

Alternatives considered:
- Allow each layer to return whichever failure it detects first without a documented priority order.
  - Rejected because that preserves inconsistent client-visible behavior.
- Hide precedence decisions entirely inside implementation code.
  - Rejected because reviewers and integrators need one documented mapping contract.

## Decision 6: Keep the implementation centered in the current protocol, hosted-entry, security, and verification seams

Rationale:
- The current client-visible code behavior is concentrated in `src/mcp_server/protocol/envelope.py`, `src/mcp_server/protocol/methods.py`, `src/mcp_server/cloud_run_entrypoint.py`, `src/mcp_server/security.py`, `src/mcp_server/tools/retrieval.py`, and the existing contract/integration tests.
- Existing verification and deployment evidence already assert client-visible code values, so those seams provide the right leverage for Red-Green-Refactor work.
- Keeping the slice in those seams avoids unnecessary architecture changes and honors the constitution’s simplicity principle.

Alternatives considered:
- Introduce a new parallel error subsystem outside the current protocol and hosted-entry flow.
  - Rejected because it would add indirection without reducing risk for this feature.
- Push all mapping changes into documentation and deployment scripts only.
  - Rejected because the codebase itself currently emits the string-coded responses that FND-018 must replace.
