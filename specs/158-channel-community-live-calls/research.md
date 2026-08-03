# Research: Layer 1 Live Calls for Channel and Community Resources

## Decision 1: Extend the existing configured runtime injection seam

**Decision**: Pass the existing `ConfiguredYouTubeRuntime` executor and configured credential availability from `InMemoryToolDispatcher` to all 20 in-scope descriptor builders, following the current `activities_list` pattern.

**Rationale**: The application already loads runtime settings, the HTTP transport already builds the configured live runtime, and the dispatcher already receives it. Only `activities_list` consumes it; the remaining 19 operations currently use family-local representative defaults. The existing descriptor builders already accept the needed executor and credential arguments.

**Alternatives considered**:

- Add a new HTTP client to each resource family: rejected because it duplicates the established shared transport and would bypass common retry, normalization, and redaction behavior.
- Teach every Layer 1 wrapper to read environment settings: rejected because it violates dependency injection and spreads secret handling across resource modules.
- Keep representative defaults for configured calls: rejected because it violates the YT-158 live execution release gate.

## Decision 2: Preserve wrappers as metadata, validation, and normalization boundaries

**Decision**: Reuse the existing resource wrappers, `EndpointMetadata`, endpoint validators, `RequestExecution`, response normalizers, and tool result/error mappers without changing their public contracts.

**Rationale**: The wrappers already validate request shape and authorization conditions before delegating to the supplied executor. The legacy `RepresentativeEndpointWrapper` type name does not require a separate execution implementation; it is the common metadata-driven wrapper. The shared executor and transport are designed to consume these existing contracts.

**Alternatives considered**:

- Rewrite the wrappers around new live-only classes: rejected because it risks 20 contract changes with no user value.
- Execute raw upstream calls directly from Layer 2 handlers: rejected because it bypasses Layer 1 validation, quota metadata, normalizers, shared retries, and safe failure mapping.
- Change public schemas or result shapes while wiring live calls: rejected because YT-158 is a retrofit, not an endpoint-inventory or MCP-contract change.

## Decision 3: Retain established authorization and request-form selection

**Decision**: Use existing selector/write rules to choose API-key, OAuth, or conditional access, and let the existing transport build query-only, JSON, raw-media, or multipart requests.

**Rationale**: Existing endpoint metadata and wrapper methods identify conditional public versus owner-scoped calls. The concrete transport already attaches an API key as a query credential or OAuth as a bearer credential and supports all request forms required by this slice.

**Alternatives considered**:

- Treat all operations as OAuth: rejected because public read operations intentionally support API-key access.
- Fall back from OAuth to an API key when a token is unavailable: rejected because OAuth-required mutations cannot safely use that fallback.
- Add resource-specific media upload logic: rejected because banner and caption uploads are already supported by the shared transport.

## Decision 4: Prove live behavior without external network access

**Decision**: Use configured runtime settings plus a controlled opener to capture generated requests and return distinctive test responses or normalized upstream failures. Add 20 request-level cases and seven public-tool flow cases.

**Rationale**: This verifies configured composition, HTTP request shape, credential mode, result mapping, error mapping, and redaction deterministically without consuming quota, relying on account state, or storing credentials in CI.

**Alternatives considered**:

- Call the live service from automated tests: rejected because it is non-deterministic, consumes quota, and introduces secret management into the test suite.
- Test only descriptor metadata: rejected because metadata tests cannot prove configured runtime selection or request construction.
- Test only the transport: rejected because it would miss the dispatcher wiring gap that causes representative defaults.

## Decision 5: Treat test/local overrides as explicit exceptions only

**Decision**: Preserve optional wrapper, executor, opener, API-key, and OAuth-token injection for isolated tests and deliberate local development, but never select them implicitly on the configured public path.

**Rationale**: Existing unit and contract tests depend on deterministic fakes. Keeping injection explicit preserves those tests while preventing a missing runtime dependency from looking like a live success.

**Alternatives considered**:

- Delete all fake transports: rejected because it would make unit tests depend on the external service.
- Return empty collections on missing configuration: rejected because callers cannot distinguish that result from a real no-match response.
- Add a feature flag that silently selects representative defaults: rejected because it obscures production behavior and violates the no-fallback requirement.

## Resolved Questions

There are no remaining `NEEDS CLARIFICATION` items. Existing YT-157 configuration, shared execution, authorization rules, request forms, safe errors, observability, and test seams define all choices needed for YT-158.
