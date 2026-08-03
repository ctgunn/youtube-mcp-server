# Research: Layer 1 Live Calls for Catalog, Membership, and Playlist Resources

## Decision 1: Extend the configured runtime injection seam

**Decision**: Pass the existing `ConfiguredYouTubeRuntime` executor and configured credential availability from `InMemoryToolDispatcher` to all 17 in-scope descriptor builders, using the existing conditional, API-key, and OAuth dependency groups.

**Rationale**: The application already loads live settings, the HTTP transport already creates the configured live runtime, and the dispatcher already receives it. The 17 affected descriptors currently omit those dependencies and therefore choose family-local representative defaults. Their descriptor builders already accept the required executor and credential values.

**Alternatives considered**:

- Add an HTTP client to every resource family: rejected because it duplicates the shared transport and bypasses common retries, normalization, observability, and redaction.
- Teach wrappers to read runtime settings: rejected because it violates dependency injection and spreads secret handling across resource modules.
- Keep representative defaults for configured calls: rejected because it violates the live-execution completion gate.

## Decision 2: Preserve wrappers as metadata, validation, and normalization boundaries

**Decision**: Reuse existing resource wrappers, endpoint metadata, validators, request executions, response normalizers, and tool result/error mappers without changing public contracts.

**Rationale**: The wrappers already validate request shape and authorization before they delegate to a supplied executor. The shared executor and transport consume those existing contracts and handle actual outbound request construction.

**Alternatives considered**:

- Replace wrappers with live-only classes: rejected because it risks 17 unnecessary contract changes.
- Make raw upstream calls from public tool handlers: rejected because it bypasses Layer 1 validation, quota metadata, normalizers, shared retries, and safe failure mapping.
- Alter public schemas or result shapes while wiring live calls: rejected because this is a retrofit, not a new endpoint or contract feature.

## Decision 3: Retain the declared authorization and request-form matrix

**Decision**: Use current endpoint and selector rules: API key for guide categories, localization, and playlist-item list; OAuth for members, membership levels, all playlist-image methods, playlist-item mutations, and playlist mutations; selector-driven API key or OAuth for playlist listing. Let the shared transport build GET/query, JSON, and multipart media forms.

**Rationale**: Existing metadata and handlers explicitly encode which inputs choose public versus owner-scoped access. The concrete transport already attaches credentials in the correct request location and supports the forms needed by this slice.

**Alternatives considered**:

- Treat every operation as OAuth: rejected because public read operations are intentionally API-key eligible.
- Fall back from unavailable OAuth to an API key: rejected because OAuth-required operations cannot safely use that fallback.
- Add playlist-image upload logic in its resource family: rejected because the common transport already builds the required multipart form.

## Decision 4: Defer missing API-key failure to the caller boundary

**Decision**: For guide-category and localization configured descriptors, use a safe deferred API-key context path if required so absent configured credentials produce an established caller-facing configuration/authentication failure at invocation time rather than failing dispatcher construction.

**Rationale**: A missing credential is an expected configured-runtime state that must fail safely and must not prevent unrelated tools from being registered. Existing handlers that resolve credentials when invoked provide the compatibility pattern.

**Alternatives considered**:

- Require an API key at dispatcher construction: rejected because a missing credential would make the service unavailable instead of exposing a safe tool-level error.
- Use a placeholder API key: rejected because it masks configuration failure and risks representative behavior.
- Remove local injected API-key support: rejected because deterministic existing tests and deliberate local use rely on explicit injection.

## Decision 5: Prove live behavior without external network access

**Decision**: Use configured runtime settings plus a controlled opener to capture generated requests and return distinctive test responses or normalized upstream failures. Add request-level coverage for all 17 operations and one configured public-tool flow per family.

**Rationale**: This deterministically proves configured composition, request shape, credential mode, result mapping, error mapping, and redaction without quota consumption, account-state dependencies, or credentials in continuous integration.

**Alternatives considered**:

- Call the live service from automated tests: rejected because it is non-deterministic, consumes quota, and introduces secrets into testing.
- Test descriptor metadata alone: rejected because it cannot prove runtime selection or request construction.
- Test only the transport: rejected because it misses the dispatcher wiring gap that causes representative defaults.

## Decision 6: Retain explicit test and local overrides only

**Decision**: Preserve optional wrapper, executor, opener, API-key, and OAuth-token injection for isolated tests and deliberate local development, but never select them implicitly on the configured public path.

**Rationale**: Existing unit and contract tests need deterministic fakes. Explicit injection preserves those tests while ensuring missing configuration cannot look like a live success.

**Alternatives considered**:

- Delete fake transports: rejected because unit tests would depend on the external service.
- Return empty collections for unavailable configuration: rejected because callers could mistake them for real no-match results.
- Add a feature flag selecting representative defaults: rejected because it obscures production behavior and violates the no-fallback requirement.

## Resolved Questions

There are no remaining `NEEDS CLARIFICATION` items. Existing YT-157 configuration, shared execution, authorization rules, request forms, safe errors, observability, and test seams define all choices needed for YT-159.
