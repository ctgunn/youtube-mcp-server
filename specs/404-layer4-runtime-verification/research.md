# Phase 0 Research: Layer 4 Configured-Runtime Capability and Live-Verification Matrix

## Decision 1: Exercise configured behavior through the existing MCP route

**Decision**: Create deterministic configured transports through `create_app` with a controlled YouTube opener, discover with `tools/list`, and invoke each matrix case with `tools/call` through `/mcp`.

**Rationale**: This reuses the actual app-to-transport-to-configured-runtime composition and MCP error mapping. Existing Layer 1 tests prove injection and request construction but call the dispatcher directly, so they do not meet the Layer 4 public-route obligation.

**Alternatives considered**:

- Call `dispatcher.call_tool` directly: rejected because it bypasses the public MCP request and result boundary.
- Construct a standalone fake runtime: rejected because it could conceal configuration-wiring regressions.

## Decision 2: Use a discovery-derived, test-owned family capability matrix

**Decision**: Maintain immutable reviewed matrix records keyed by YouTube resource family, tool name, safe arguments, selected credential state, expected capability outcome, and safe request expectation. Derive the family inventory from discovery metadata and fail on missing or stale family records.

**Rationale**: The current default catalog has 72 YouTube descriptors spanning 22 families, with conditional tools requiring deliberate public or owner-scoped selector choices. Test-owned records make those choices reviewable without duplicating the public tool catalog.

**Alternatives considered**:

- Generate matrix inputs from schemas or infer capability from tool names: rejected because schemas and names cannot select safe conditional paths or reliably identify owner-sensitive behavior.
- Maintain an independent list of all public tool names: rejected because discovery remains the authority for catalog membership.

## Decision 3: Explicitly exclude non-YouTube tools from capability coverage

**Decision**: Classify the generic `server_ping`, `server_info`, `server_list_tools`, `search`, and `fetch` descriptors as out of scope for the configured YouTube matrix; the coverage report must state that exclusion.

**Rationale**: These five descriptors do not have a configured YouTube credential boundary. Treating them as unavailable YouTube cases would create misleading verification results.

**Alternatives considered**:

- Include all catalog tools as unavailable cases: rejected because it falsely reports an absent YouTube capability for unrelated tools.
- Ignore them without reporting: rejected because it weakens reviewability of matrix scope.

## Decision 4: Prove live-runtime selection with a controlled, sanitized opener

**Decision**: Inject an opener that captures only tool/family, request path shape, HTTP method, selected credential mode, and bounded call count; it returns a controlled response and never contacts the network. The suite also patches socket and URL-opening paths to fail on unplanned I/O.

**Rationale**: The real configured executor builds requests through the injected opener, so one safe record proves live-runtime selection without a real credential or external quota use. Capturing raw URLs, headers, or bodies would risk secret disclosure.

**Alternatives considered**:

- Use a real API key and service call: rejected because deterministic matrix tests must be safe, repeatable, and offline.
- Assert handler closure values only: rejected because dependency injection alone does not prove request construction through MCP.

## Decision 5: Classify missing capabilities using existing safe MCP errors

**Decision**: For a missing API key, expect the safe authentication failure category; for missing OAuth authority, expect the safe authorization failure category; for conditional tools, select reviewed arguments that resolve the intended capability before invocation. Assert errors from the public MCP route and no controlled request record.

**Rationale**: `ConfiguredYouTubeRuntime.auth_context_for` already emits caller-safe categories and the protocol route maps tool failures into MCP-safe error envelopes. The matrix must prove this behavior does not fall back to representative local data.

**Alternatives considered**:

- Treat all unavailable outcomes as generic internal failures: rejected because it loses actionable capability information.
- Assert local representative error results: rejected because configured mode must not fabricate local data.

## Decision 6: Make the live smoke workflow explicit, local, and allowlisted

**Decision**: Extend the existing `scripts/verify_youtube_live.py` and its opt-in test with a reviewed API-key public-read allowlist, initially retaining only the current language-list operation. Perform enablement and credential checks before app construction, validate discovery membership, invoke through MCP, bound requests and timeouts, and produce separate safe results for selected and excluded tools.

**Rationale**: The existing smoke flow already requires `RUN_YOUTUBE_LIVE_SMOKE=1` plus an API key and calls a read-only endpoint, but it has no maintained allowlist, per-tool report, bounded policy, or safe raw-exception boundary. A small explicit allowlist prevents accidental invocation of mutations or sensitive reads.

**Alternatives considered**:

- Select tools based on a `list` suffix or metadata that appears read-like: rejected because read operations can still be OAuth-, owner-, or resource-sensitive.
- Expand immediately to all read-like public tools: rejected because each live input and upstream impact requires review.
- Implement remote server smoke: rejected because OPS-405 owns public remote MCP endpoint verification.

## Decision 7: Keep live smoke outside ordinary quality gates

**Decision**: Add separate `make test-runtime` and `make test-live-smoke` commands; keep `make test-tools`, `make test`, `make quality`, CI, and automated deployment free of live smoke execution.

**Rationale**: Configured-runtime tests are deterministic and offline, whereas live smoke requires operator credentials, consumes quota, and depends on upstream availability.

**Alternatives considered**:

- Include live smoke in `make test` or `make quality`: rejected because it risks accidental calls, secret handling, quota consumption, and flaky CI/deployment gates.
- Provide only a raw script command: rejected because stable project commands and clear documentation reduce operator error.

## Decision 8: Use fixed, credential-safe reporting at the CLI boundary

**Decision**: Report only allowlisted tool identity, classification, item/count summary, and safe failure category or message. Never interpolate arbitrary exception text into console output or persisted evidence.

**Rationale**: Current script output interpolates exception text, which becomes unsafe as the workflow expands. Existing error sanitization conventions protect structured details; the final CLI boundary must preserve that protection.

**Alternatives considered**:

- Print raw exception strings for diagnosis: rejected because upstream or transport exceptions can contain credentials, URLs, headers, or response bodies.
- Persist complete upstream payloads for debugging: rejected because they can expose sensitive data and are unnecessary for smoke evidence.
