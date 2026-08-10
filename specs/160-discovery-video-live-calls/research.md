# Research: Layer 1 Discovery, Video, and Branding Live-Call Retrofit

## Decision 1: Reuse the configured runtime dependency-injection seam

**Decision**: Pass the existing YT-157 `ConfiguredYouTubeRuntime` executor and the applicable configured credentials from `InMemoryToolDispatcher` to every in-scope descriptor.

**Rationale**: Application composition and the HTTP transport already construct this runtime, which contains the concrete authenticated YouTube transport, configured timeout, shared retries, error normalization, and safe observability hooks. The dispatcher uses conditional, API-key, and OAuth dependency groups for all YouTube Data API-backed descriptors; the original 16 YT-160 descriptors remain the regression subset for this retrofit.

**Alternatives considered**:

- Add a resource-specific HTTP client: rejected because it duplicates transport, retry, credential, error, and observability behavior.
- Make wrappers read runtime settings directly: rejected because it spreads secret handling across resource modules and breaks dependency injection.
- Keep representative defaults for configured calls: rejected because it violates the live-execution completion gate.

## Decision 2: Preserve wrappers as metadata, validation, and normalization boundaries

**Decision**: Reuse existing resource wrappers, endpoint metadata, validators, request executions, response normalizers, and tool result/error mappers without changing public contracts.

**Rationale**: The wrappers already validate request shape and authorization before delegating to a supplied executor. The shared executor and transport consume those contracts and handle actual outbound request construction.

**Alternatives considered**:

- Replace wrappers with live-only classes: rejected because it risks unnecessary contract changes across 16 operations.
- Make raw upstream calls from public tool handlers: rejected because it bypasses Layer 1 validation, quota metadata, normalizers, shared retries, and safe failure mapping.
- Alter public schemas or result shapes while wiring live calls: rejected because this is a retrofit, not a public endpoint feature.

## Decision 3: Use the existing authorization and request-form matrix

**Decision**: Preserve selector and operation rules: conditional API-key or OAuth selection for `search.list`, `subscriptions.list`, and `videos.list`; API-key access for video abuse-reason and video-category lists; and OAuth for subscription writes, thumbnail, video mutation/rating, and watermark operations. Let the shared transport build query-only, JSON, raw-media, and multipart requests.

**Rationale**: Existing metadata and handlers explicitly encode which inputs select public versus owner-scoped access. The common transport attaches credentials in the required request location and supports the existing media forms.

**Alternatives considered**:

- Treat every operation as OAuth: rejected because eligible public reads must retain API-key access.
- Fall back from unavailable OAuth to an API key: rejected because OAuth-required operations cannot safely use that fallback.
- Add media logic in a resource family: rejected because the common transport already handles media serialization.

## Decision 4: Inject the configured lower-level lookup into `videos_getVideo`

**Decision**: Build the composed video-detail descriptor with a lookup created from the configured `videos.list` handler and its conditional dependencies.

**Rationale**: The composed handler currently defaults to a separately constructed `videos.list` handler, which selects local defaults. It is a composition-only tool and must continue to delegate to the lower-level live wrapper rather than issue its own direct request.

**Alternatives considered**:

- Add direct YouTube HTTP logic to the composed tool: rejected because it bypasses Layer 1 and violates the stated dependency boundary.
- Change the detail tool's public request or result contract: rejected because no public contract change is required.
- Leave the default lookup unmodified: rejected because it leaves a configured public flow representative-backed.

## Decision 5: Extend the shared transport with Google upload protocols

**Decision**: Keep all media behavior in the shared transport. Direct raw-media requests use `/upload/youtube/v3/...` with `uploadType=media`; metadata-plus-media uses `uploadType=multipart`; and `videos.insert` with `uploadMode=resumable` creates and uses a resumable Google upload session.

**Rationale**: Google treats media uploads as a distinct transport protocol. Implementing it once in the shared transport preserves wrapper contracts and avoids resource-family HTTP clients while making every advertised upload form conform to the Data API protocol.

**Alternatives considered**:

- Keep `uploadMode=resumable` as a query parameter: rejected because it does not create a resumable session and falsely advertises support.
- Remove `uploadMode=resumable`: rejected because the shared transport can implement the protocol without a public contract regression.
- Add video-family upload logic: rejected because it would duplicate credential, error, retry, and redaction behavior.

## Decision 6: Prove configured live behavior with controlled openers

**Decision**: Use configured runtime settings plus a controlled opener to capture generated requests and return distinctive test responses or normalized upstream failures. Preserve the 16-operation and three-public-flow regression matrix, then add focused transport tests for OAuth renewal, Google upload routing, resumable chunks/recovery, and retry safety.

**Rationale**: This proves composition, request shape, credential mode, result mapping, error mapping, retry behavior, and redaction deterministically without external network calls, quota usage, account-state dependencies, or secrets in continuous integration.

**Alternatives considered**:

- Call the live service from automated tests: rejected because it is non-deterministic, consumes quota, and requires secrets.
- Test descriptor metadata alone: rejected because it cannot prove runtime selection or request construction.
- Test only the common transport: rejected because it misses the dispatcher and composed-tool gaps that select representative defaults.

## Decision 7: Support renewable OAuth without widening the credential boundary

**Decision**: Accept either a static OAuth access token or a complete refresh-token credential set. The runtime refreshes and caches access tokens in memory, while all long-lived credentials remain operator-managed secrets.

**Rationale**: A static token cannot sustain owner and mutation operations in a hosted deployment. Refresh support keeps secret ownership outside tools and responses while avoiding an external credential store.

**Alternatives considered**:

- Require only static tokens: rejected because expiry would make hosted operation unreliable.
- Persist access or refresh tokens in application storage: rejected because YT-160 requires environment/secret-backed credentials and no persistent credential store.

## Decision 8: Limit automatic retries to idempotent requests

**Decision**: Use bounded full-jitter exponential backoff only for `GET`, `HEAD`, `PUT`, and `DELETE`; do not retry POST mutations automatically.

**Rationale**: Full jitter prevents synchronized retry bursts after shared rate limits or outages, while a transport error after a POST can occur after YouTube has already applied a mutation. Conservatively avoiding replay prevents duplicate user-visible side effects.

## Decision 9: Retain explicit test and local overrides only

**Decision**: Preserve optional wrapper, executor, opener, API-key, OAuth-token, and composed lookup injection for isolated tests and deliberate local development, but never select them implicitly in configured public composition.

**Rationale**: Existing unit and contract tests need deterministic fakes. Explicit injection preserves those tests while ensuring missing configuration cannot look like a live success.

**Alternatives considered**:

- Delete fake transports: rejected because unit tests would depend on the external service.
- Return empty collections for unavailable configuration: rejected because callers could mistake them for real no-match results.
- Add a feature flag selecting representative defaults: rejected because it obscures production behavior and violates the no-fallback requirement.

## Resolved Questions

All research questions are resolved. YT-160 now owns the shared live-execution completion gate: configured runtime composition, safe credential lifecycle, Google upload protocols, method-safe retry behavior, readiness capability reporting, deterministic protocol tests, and an operator-gated real smoke check.
