# Research: Initialize Session Correctness

## Decision 1: Gate session creation on successful initialize completion

- **Decision**: Treat session creation and `MCP-Session-Id` issuance as a post-success action that runs only after the hosted initialize request returns a successful protocol result.
- **Rationale**: The current hosted executor in `src/mcp_server/cloud_run_entrypoint.py` creates a session immediately after any `initialize` request is routed, even if the protocol response contains an error. FND-024 exists specifically to close that gap. Moving session creation behind initialize success enforces the intended lifecycle without changing the transport shape.
- **Alternatives considered**:
  - Keep creating sessions before validation and try to clean them up after failure. Rejected because it leaves a window for invalid continuation state and adds unnecessary cleanup complexity.
  - Preserve the current behavior and document it. Rejected because it directly contradicts the feature specification and acceptance criteria.

## Decision 2: Treat any initialize response carrying a protocol error as a failed initialize path

- **Decision**: Define a failed initialize path as any hosted initialize request that returns a protocol error response or is rejected earlier by hosted validation, security, or protocol-version checks.
- **Rationale**: From the client’s perspective, malformed JSON, invalid initialize params, unsupported protocol version, missing authentication, and origin denial are all initialize attempts that did not establish a usable hosted session. FND-024 needs one consistent rule: no successful initialize result means no session header and no continuation state.
- **Alternatives considered**:
  - Restrict the rule to protocol-level validation failures only. Rejected because security or hosted-routing rejections would still leave ambiguity about whether a session might exist.
  - Distinguish “pre-protocol” initialize failures from “protocol” initialize failures in the contract. Rejected because the external requirement is simpler: rejected initialize requests never establish sessions.

## Decision 3: Successful retries after failed initialize must create fresh valid state

- **Decision**: If a client retries initialize after one or more failures, only the later successful attempt may create a hosted session, and that session must not depend on any state from prior failed attempts.
- **Rationale**: The spec explicitly requires session state to reflect valid lifecycle progress. Retrying initialize is normal client behavior, especially after malformed requests, credential issues, or dropped responses. The cleanest contract is that failed attempts create nothing reusable, while the first later success creates exactly one valid session.
- **Alternatives considered**:
  - Cache partially initialized state across retries. Rejected because it complicates lifecycle reasoning and increases the chance of invalid continuation behavior.
  - Require clients to use the same request identifier when retrying. Rejected because the feature does not depend on request-id idempotency semantics.

## Decision 4: Keep the fix in the hosted request executor rather than redesigning protocol routing

- **Decision**: Implement the lifecycle correction at the hosted initialize/session boundary in `src/mcp_server/cloud_run_entrypoint.py`, with any small shared helper needed to recognize a successful initialize result safely.
- **Rationale**: The protocol router in `src/mcp_server/protocol/methods.py` already returns a success response for valid initialize and error responses for invalid initialize. The bug is introduced when hosted request handling creates the session unconditionally after routing. Fixing the decision where session headers are emitted is the smallest safe change and matches the constitution’s simplicity rule.
- **Alternatives considered**:
  - Move session creation into the protocol router. Rejected because session persistence and HTTP headers are hosted transport concerns, not protocol-payload concerns.
  - Add a separate session-validation middleware. Rejected because it spreads one lifecycle rule across more layers than necessary.

## Decision 5: Hosted verification must prove both absence and presence of session issuance

- **Decision**: Extend hosted verification, contract tests, and integration tests so they prove both that failed initialize requests return no `MCP-Session-Id` and that successful initialize requests still return exactly one session identifier.
- **Rationale**: This repository treats hosted verification as part of the public MCP contract, not just as an internal smoke test. FND-024 can regress silently if only the success path is tested. The verifier and docs-backed checks must show the negative lifecycle guarantee explicitly.
- **Alternatives considered**:
  - Rely on unit tests alone. Rejected because the externally visible behavior includes headers, session continuation, and hosted verification evidence.
  - Verify only malformed initialize failures. Rejected because invalid params and security denials also matter to the external lifecycle boundary.

## Decision 6: Preserve existing security and session-state failure categories

- **Decision**: Keep existing authentication, origin, invalid-session, expired-session, and replay-unavailable behavior intact while tightening only the session-creation gate for initialize.
- **Rationale**: FND-024 is a correctness slice, not a new security or session-durability feature. Preserving the current failure taxonomy reduces regression risk and keeps the change narrowly focused on when continuation state may begin.
- **Alternatives considered**:
  - Redefine invalid-session or initialize error categories at the same time. Rejected because that would enlarge the feature and blur the acceptance criteria.
  - Introduce a new “initialize_failed_session” category. Rejected because the better behavior is to avoid creating a session at all.

## Decision 7: Observability must distinguish rejected initialize from valid continuation

- **Decision**: Maintain or extend session-decision logging so operators can distinguish initialize rejection without session creation from valid continuation and later invalid-session failures.
- **Rationale**: The repo already emits session decision events. FND-024 affects a lifecycle boundary that operators may need to diagnose in hosted environments. Verification artifacts and logs should show whether a session was never created, created successfully, or rejected later during continuation.
- **Alternatives considered**:
  - Make no observability changes and rely on test evidence alone. Rejected because production diagnosis would remain harder than necessary.
  - Emit full request payloads for rejected initialize requests. Rejected because it risks exposing unsafe details and is unnecessary for this correction.

## Sources

- `src/mcp_server/cloud_run_entrypoint.py`
- `src/mcp_server/protocol/methods.py`
- `src/mcp_server/transport/streaming.py`
- `tests/contract/test_streamable_http_contract.py`
- `tests/contract/test_hosted_mcp_security_contract.py`
- `tests/integration/test_hosted_http_routes.py`
- `tests/integration/test_streamable_http_transport.py`
- `tests/integration/test_cloud_run_verification_flow.py`
- `scripts/verify_cloud_run_foundation.py`
