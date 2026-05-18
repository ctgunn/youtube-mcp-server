# Research: YT-154 Layer 1 Endpoint `watermarks.set`

## Decision: Model `watermarks.set` as an OAuth-required media-upload mutation wrapper with required channel, watermark metadata, and media inputs

**Rationale**: Local product artifacts define YT-154 as a typed Layer 1 wrapper for the YouTube Data API `watermarks.set` endpoint with visible media-upload and OAuth expectations and a 50-unit quota cost. Official Google documentation identifies `channelId` as a required query parameter, requires a `watermark` resource in the request body, supports media upload, and requires OAuth authorization. Adjacent upload wrappers such as `thumbnails.set`, `channelBanners.insert`, and playlist-image mutations keep required identifiers, body metadata, media payloads, auth mode, and quota cost explicit before execution. The smallest consistent fit is therefore a wrapper that requires a non-empty `channelId`, one supported watermark resource body, one supported `media` upload payload, and OAuth-backed access.

**Alternatives considered**: Accepting media-only watermark requests was rejected because the endpoint also requires channel targeting and watermark metadata. Accepting metadata-only requests was rejected because the endpoint is a media upload operation. Treating channel selection as implicit from credentials was rejected because the official contract requires `channelId`. Treating the endpoint as API-key compatible was rejected because the endpoint requires authorized access.

## Decision: Use the documented upload endpoint and keep media constraints visible

**Rationale**: Official Google documentation gives the upload request path as `POST https://www.googleapis.com/upload/youtube/v3/watermarks/set`, lists a maximum file size of 10 MB, and lists supported media MIME types as JPEG, PNG, and `application/octet-stream`. Local upload wrappers already use a `media` payload convention to keep upload content distinct from resource metadata. YT-154 should preserve that convention while recording the upload-specific path shape and media constraints in metadata, contracts, docstrings, and tests.

**Alternatives considered**: Reusing a non-upload `/youtube/v3/watermarks/set` path was rejected because the official method is media-upload based. Accepting arbitrary MIME types or unlimited content was rejected because it would hide documented upstream constraints and produce less useful validation failures. Encoding media bytes in review artifacts was rejected because uploaded content should not appear in docs, logs, summaries, or fixtures beyond safe placeholder examples.

## Decision: Normalize HTTP 204 no-content success into a watermark-update acknowledgement

**Rationale**: Official Google documentation states that a successful `watermarks.set` call returns HTTP 204 with no content. Existing delete and upload mutation slices normalize empty or near-empty successful responses into acknowledgement-style results that preserve source operation, target input, quota cost, auth mode, and review notes. YT-154 should follow that pattern so downstream layers do not infer success from an empty response and do not need to inspect transport-level details.

**Alternatives considered**: Returning an empty mapping was rejected because it is ambiguous for higher layers and does not satisfy the spec's request-context preservation requirement. Fetching channel branding state after the set call was rejected because successful watermark setting should not require a second read operation in this slice.

## Decision: Keep `onBehalfOfContentOwner` visible but outside the guaranteed supported boundary unless deliberately implemented in the wrapper

**Rationale**: Official Google documentation lists `onBehalfOfContentOwner` as an optional query parameter intended exclusively for YouTube content partners. This parameter expands authorization semantics beyond ordinary OAuth-backed channel watermark updates. The YT-154 feature spec asks for the typed wrapper, quota cost, media-upload requirement, and OAuth requirement, not partner delegation. The plan should therefore require the contract to mention the partner-only parameter and require unsupported partner delegation to be rejected or clearly flagged unless implementation tasks deliberately add it as a supported optional field.

**Alternatives considered**: Fully supporting `onBehalfOfContentOwner` by default was rejected because it broadens security review and test obligations. Ignoring the parameter was rejected because later maintainers need to know whether partner delegation is supported or outside the slice.

## Decision: Separate invalid request, access failure, unsupported media, invalid watermark image, forbidden channel, upstream unavailable, and successful acknowledgement outcomes

**Rationale**: The repository already uses wrapper-level validation and normalized upstream failures to keep local request problems distinct from runtime failures. Official Google documentation identifies errors for unsupported image format, oversized dimensions, missing media body, and forbidden channel/update scenarios. Because this is an upload mutation with a 50-unit quota cost, the plan must preserve a clear difference between malformed local input, missing OAuth-backed access, unsupported media, upstream image validation, channel authorization or eligibility failure, transient upstream failure, and successful watermark acknowledgement.

**Alternatives considered**: Collapsing all watermark failures into a generic upstream error was rejected because calling workflows need to know whether to correct input, obtain different authorization, adjust uploaded image content, retry later, or surface an upstream refusal.

## Decision: Reuse existing Layer 1 wrapper, upload, transport, consumer-summary, and test seams

**Rationale**: Adjacent endpoint slices expose the wrapper contract in three places: `review_surface()` metadata from the wrapper, feature-local contracts under `specs/<feature>/contracts/`, and higher-layer summary fields in `consumer.py` that keep source operation, quota, auth mode, and request-boundary notes visible without reading lower-level code. YT-154 should follow that same pattern by adding a `watermarks.set` review surface, wrapper contract plus auth-upload contract, and a summary path that echoes channel id, acknowledgement state, source contract details, and absence of credential or media-byte exposure.

**Alternatives considered**: Creating a new upload abstraction was rejected because existing upload wrappers already provide the required seams. Skipping consumer-summary coverage was rejected because nearby Layer 1 slices use it to prove downstream reviewability before public tools are introduced.

## Sources

- `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/154-watermarks-set-wrapper/spec.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- Official Google reference: https://developers.google.com/youtube/v3/docs/watermarks/set
