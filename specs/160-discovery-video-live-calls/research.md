# Research: Layer 1 Discovery, Video, and Branding Live-Call Retrofit

## Decision 1: Reuse the configured runtime dependency-injection seam

**Decision**: Pass the existing YT-157 `ConfiguredYouTubeRuntime` executor and the applicable configured credentials from `InMemoryToolDispatcher` to every in-scope descriptor.

**Rationale**: Application composition and the HTTP transport already construct this runtime, which contains the concrete authenticated YouTube transport, configured timeout, shared retries, error normalization, and safe observability hooks. The dispatcher already uses conditional, API-key, and OAuth dependency groups for earlier resource-family retrofits. The 16 YT-160 descriptors are currently the unconnected group.

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

## Decision 5: Preserve current shared media behavior; do not add a resumable protocol

**Decision**: Test the existing shared request behavior for thumbnail, video, and watermark media inputs. Retain `videos.insert` upload-mode validation and metadata, but do not add a resumable-session protocol in this wiring retrofit.

**Rationale**: The feature requires shared upload execution and forbids resource-specific clients. The common transport already builds the established raw-media and multipart payloads from validated inputs. A resumable-session protocol is a distinct transport capability, not required to connect configured defaults to the runtime.

**Alternatives considered**:

- Add video-family resumable logic: rejected because it would be a second transport path and expands feature scope.
- Remove the accepted upload-mode value: rejected because it changes the existing public contract.
- Skip media request coverage: rejected because the seed requires request-form proof for media-bearing methods.

## Decision 6: Prove configured live behavior with controlled openers

**Decision**: Use configured runtime settings plus a controlled opener to capture generated requests and return distinctive test responses or normalized upstream failures. Cover all 16 operations and the three named public-tool flows.

**Rationale**: This proves composition, request shape, credential mode, result mapping, error mapping, retry behavior, and redaction deterministically without external network calls, quota usage, account-state dependencies, or secrets in continuous integration.

**Alternatives considered**:

- Call the live service from automated tests: rejected because it is non-deterministic, consumes quota, and requires secrets.
- Test descriptor metadata alone: rejected because it cannot prove runtime selection or request construction.
- Test only the common transport: rejected because it misses the dispatcher and composed-tool gaps that select representative defaults.

## Decision 7: Retain explicit test and local overrides only

**Decision**: Preserve optional wrapper, executor, opener, API-key, OAuth-token, and composed lookup injection for isolated tests and deliberate local development, but never select them implicitly in configured public composition.

**Rationale**: Existing unit and contract tests need deterministic fakes. Explicit injection preserves those tests while ensuring missing configuration cannot look like a live success.

**Alternatives considered**:

- Delete fake transports: rejected because unit tests would depend on the external service.
- Return empty collections for unavailable configuration: rejected because callers could mistake them for real no-match results.
- Add a feature flag selecting representative defaults: rejected because it obscures production behavior and violates the no-fallback requirement.

## Resolved Questions

All research questions are resolved. Existing YT-157 runtime configuration, shared execution, authorization rules, request forms, error normalization, observability, and test seams define all choices required for YT-160.
