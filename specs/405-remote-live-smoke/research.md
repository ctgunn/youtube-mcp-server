# Phase 0 Research: Layer 4 Remote MCP Read-Only Live Smoke

## Decision 1: Use a separate remote HTTP client

**Decision**: Add a small, injectable standard-library HTTP client in a dedicated remote-smoke script. It connects only to the operator-supplied remote MCP URL and never creates an application instance or calls a dispatcher.

**Rationale**: The feature must prove the deployed public transport, authentication, session continuity, handlers, and configured YouTube execution path. The existing local smoke deliberately constructs an in-process application and therefore cannot meet this boundary.

**Alternatives considered**:

- Reuse the local in-process smoke transport: rejected because it bypasses the running remote server.
- Add a general-purpose external MCP client dependency: rejected because the required interaction is small and the standard library already supports the established hosted request behavior.

## Decision 2: Follow the hosted initialize-session-call sequence

**Decision**: Send `initialize` with client information, retain the successful response's `MCP-Session-Id` and protocol version, then send `tools/list` and selected `tools/call` requests with those values. Include bearer authorization on every request only when the target endpoint requires it.

**Rationale**: The current hosted server creates the session only after successful initialization and requires its session identifier for continuations. Authentication is evaluated before session handling, so every public request must carry the needed credential.

**Alternatives considered**:

- Issue discovery or calls without initialization/session retention: rejected because a hosted server correctly rejects those requests.
- Open a server-event stream for the smoke: rejected because server-push/reconnect behavior is outside this bounded baseline; POST responses exercise the required call route.

## Decision 3: Safely support direct JSON and streamed call responses

**Decision**: Treat direct JSON as the discovery response format and normalize a `tools/call` streamed response by parsing only the JSON-RPC event for the call request. The parser will return a sanitized protocol envelope and will not retain or print raw body text.

**Rationale**: The hosted transport can return an event stream for calls even though initialization and discovery are direct JSON. Supporting both expected forms proves the real public route without requiring a persistent event stream.

**Alternatives considered**:

- Assume every response is JSON: rejected because it would fail against the hosted call transport.
- Persist complete response text for troubleshooting: rejected because upstream data and errors can contain sensitive or unnecessary content.

## Decision 4: Reuse the reviewed 12-entry public-read allowlist

**Decision**: Reuse the existing ordered explicit allowlist of 12 reviewed API-key public-read operations, their bounded public inputs, expected upstream operations, request bound, and one approved in-memory comment-parent fixture dependency. Discovery determines whether an approved entry is present; it does not grant approval to new tools.

**Rationale**: These entries have already been reviewed for API-key capability, read-only behavior, and live-safe public fixtures. A maintained list is auditable and prevents a newly discovered operation from being invoked accidentally.

**Alternatives considered**:

- Select every tool with a `list` suffix or read-like metadata: rejected because those properties do not establish credential mode, ownership sensitivity, or write safety.
- Duplicate all discovered tool names in the remote client: rejected because discovery must remain the catalog authority and duplicate lists drift.

## Decision 5: Enforce finite work at both protocol and HTTP layers

**Decision**: Cap each run at 12 selected tool calls, plus one initialization and one discovery request, for at most 14 POSTs. Apply a 30-second timeout to each HTTP request; when a tool cannot start because a bound is reached, report it as bound reached rather than retrying.

**Rationale**: The current reviewed allowlist has 12 entries and each is one bounded call. A finite remote timeout gives operators predictable completion even if an endpoint or upstream provider is unavailable.

**Alternatives considered**:

- Retry indefinitely for transient remote failures: rejected because it can consume quota and obscure the original failure.
- Use an unbounded catalog-driven loop: rejected because a catalog expansion must receive explicit fixture/safety review before it is live-callable.

## Decision 6: Use fixed, credential-safe classification and evidence

**Decision**: Report only tool identity, terminal outcome, safe category, approved endpoint identity, item count where safe, exclusion count, and request bounds. Map preflight/transport/protocol failures to fixed safe categories and never interpolate exception text or copy request/response details.

**Rationale**: Tokens, authorization headers, session IDs, derived identifiers, full URLs, and upstream bodies can leak through raw HTTP errors or diagnostics. Per-tool safe categories still make failures actionable.

**Alternatives considered**:

- Print raw exception messages and headers for diagnosis: rejected because they can disclose credentials and request data.
- Mark every non-success as a generic pass/fail: rejected because operators need to distinguish documented safe availability from actionable remote or contract failures.

## Decision 7: Validate endpoint identity against discovery metadata

**Decision**: For a successful structured result that declares `endpoint`, require agreement with both the reviewed allowlist expectation and the discovered descriptor's `metadata.upstream.operationKey` when that metadata is present. Report disagreement as an actionable failure.

**Rationale**: This proves that the discovered public tool and the selected live execution path agree, without snapshotting upstream data.

**Alternatives considered**:

- Assert only a non-error response: rejected because it does not detect a mismatched handler/descriptor path.
- Require endpoint metadata for every tool: rejected because conditional validation is needed where the descriptor does not publish it.

## Decision 8: Keep remote smoke a manual fourth verification boundary

**Decision**: Add a manual `make test-remote-live-smoke` target that is explicitly opt-in and remains outside `make test`, `make quality`, CI, and automated deployments. README will distinguish it from deterministic catalog coverage, configured-runtime verification, and local live smoke.

**Rationale**: Remote live smoke requires endpoint approval and credentials, consumes external quota, and depends on upstream availability. It complements rather than replaces deterministic coverage.

**Alternatives considered**:

- Include it in normal quality or deployment validation: rejected because it introduces credentials, quota use, and upstream flakiness into ordinary automation.
- Provide only an undocumented raw script: rejected because a stable command and documented safety process reduce operator error.
