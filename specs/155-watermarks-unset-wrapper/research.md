# Research: YT-155 Layer 1 Endpoint `watermarks.unset`

## Decision: Model `watermarks.unset` as an OAuth-required channel-targeted mutation wrapper

**Rationale**: Local product artifacts define YT-155 as a typed Layer 1 wrapper for the YouTube Data API `watermarks.unset` endpoint with visible OAuth expectations and a 50-unit quota cost. The PRD includes `watermarks.unset` in the required Layer 1 inventory, and the seed identifies the upstream request as `POST /watermarks/unset`. Adjacent mutation wrappers keep required identifiers, auth mode, quota cost, and normalized results explicit before execution. The smallest consistent fit is therefore a wrapper that requires a non-empty `channelId` and OAuth-backed access.

**Alternatives considered**: Treating channel selection as implicit from credentials was rejected because the spec requires enough channel context for downstream interpretation and local validation. Treating the endpoint as API-key compatible was rejected because the seed requires OAuth documentation. Requiring watermark body or media upload inputs was rejected because those belong to `watermarks.set`, not `watermarks.unset`.

## Decision: Use a no-upload request boundary and reject watermark-setting payloads for unset

**Rationale**: `watermarks.unset` removes a channel watermark rather than uploading or replacing one. The adjacent `watermarks.set` slice deliberately requires `body` and `media`, but YT-155 explicitly centers on the unset operation and the spec states that media upload content and watermark placement metadata are outside this wrapper's supported request contract. Keeping the no-upload boundary visible prevents callers from assuming unset can accept set-style metadata.

**Alternatives considered**: Silently ignoring `body` or `media` was rejected because it makes request intent ambiguous and could hide caller mistakes. Reusing the upload path or upload validation from `watermarks.set` was rejected because it would blur two different endpoint contracts.

## Decision: Normalize empty successful responses into a watermark-removal acknowledgement

**Rationale**: Nearby mutation and delete slices normalize empty successful upstream responses into acknowledgement-style results that preserve source operation, target input, quota cost, auth mode, and review notes. YT-155 should follow that pattern so downstream layers do not infer success from an empty response and do not need to inspect transport-level details.

**Alternatives considered**: Returning an empty mapping was rejected because it is ambiguous for higher layers and does not satisfy the spec's request-context preservation requirement. Fetching channel branding state after the unset call was rejected because successful watermark removal should not require a second read operation in this slice.

## Decision: Keep `onBehalfOfContentOwner` visible but outside the guaranteed supported boundary unless deliberately implemented in the wrapper

**Rationale**: Partner-only delegated content-owner context expands authorization semantics beyond ordinary OAuth-backed channel watermark removal. The YT-155 feature spec asks for the typed wrapper, quota cost, and OAuth requirement, not partner delegation. The plan should therefore require the contract to mention this boundary and require delegated partner input to be rejected or clearly flagged unless implementation tasks deliberately add it as a supported optional field.

**Alternatives considered**: Fully supporting delegated content-owner input by default was rejected because it broadens security review and test obligations. Ignoring the possibility was rejected because later maintainers need to know whether delegated behavior is supported or outside the slice.

## Decision: Separate invalid request, access failure, forbidden channel, no-removal-possible, upstream unavailable, and successful acknowledgement outcomes

**Rationale**: The repository already uses wrapper-level validation and normalized upstream failures to keep local request problems distinct from runtime failures. Because `watermarks.unset` is an authorization-sensitive mutation with a 50-unit quota cost, the plan must preserve a clear difference between malformed local input, missing OAuth-backed access, channel authorization or eligibility failure, no-current-watermark or already-removed outcomes, transient upstream failure, and successful watermark-removal acknowledgement.

**Alternatives considered**: Collapsing all watermark removal failures into a generic upstream error was rejected because calling workflows need to know whether to correct input, obtain different authorization, retry later, or surface a no-removal/forbidden upstream refusal.

## Decision: Reuse existing Layer 1 wrapper, transport, consumer-summary, and test seams

**Rationale**: Adjacent endpoint slices expose the wrapper contract in three places: `review_surface()` metadata from the wrapper, feature-local contracts under `specs/<feature>/contracts/`, and higher-layer summary fields in `consumer.py` that keep source operation, quota, auth mode, and request-boundary notes visible without reading lower-level code. YT-155 should follow that same pattern by adding a `watermarks.unset` review surface, wrapper contract plus auth-boundary contract, and a summary path that echoes channel id, removal acknowledgement state, source contract details, and absence of credential exposure.

**Alternatives considered**: Creating a new mutation abstraction was rejected because existing mutation wrappers already provide the required seams. Skipping consumer-summary coverage was rejected because nearby Layer 1 slices use it to prove downstream reviewability before public tools are introduced.

## Sources

- `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/requirements/PRD.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/155-watermarks-unset-wrapper/spec.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/154-watermarks-set-wrapper/`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
