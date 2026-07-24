# Research: Layer 2 Tool `watermarks_set`

## Decision: Add a new Python Layer 2 watermarks module

**Rationale**: The local Layer 2 package already lists the `watermarks` resource family, but there is no concrete `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py` module. Adding `watermarks_set` there keeps endpoint-backed `watermarks.*` tools cohesive and lets the feature reuse shared Layer 2 contract primitives, response boundaries, safe error handling, examples, public exports, and default dispatcher registration patterns.

**Alternatives considered**: Adding watermark setting to `thumbnails.py`, `channel_banners.py`, `channels.py`, or `videos.py` was rejected because this is a distinct upstream `watermarks` resource. Creating a higher-level branding module was rejected because YT-254 is a low-level Layer 2 endpoint tool.

## Decision: Reuse YT-154 `build_watermarks_set_wrapper()`

**Rationale**: The local Layer 1 dependency already exposes `watermarks.set` with operation key `watermarks.set`, `POST /upload/youtube/v3/watermarks/set`, quota cost `50`, OAuth-required access, required `channelId`, required `body`, required `media`, accepted MIME types, 10 MB upload boundary, rejected unsupported top-level fields, rejected partner-only delegation in this slice, and normalized watermark-update acknowledgment support. YT-254 should expose that capability publicly through Layer 2 without redefining upstream execution, auth, quota, or base validation behavior.

**Alternatives considered**: Reimplementing upstream upload request construction in Layer 2 was rejected because it would duplicate Layer 1 behavior. Expanding Layer 1 to include partner delegation is out of scope unless implementation reveals a deliberately approved narrow contract expansion.

## Decision: Public identity and metadata

**Rationale**: The public tool must be named `watermarks_set`, mapped to upstream resource `watermarks` and method `set`, and show operation key `watermarks.set`. Discovery metadata, descriptions, usage notes, and examples must expose quota cost `50`, OAuth-only access, required `channelId`, required watermark `body`, required `media`, accepted upload boundary, sparse acknowledgment semantics, rejected partner delegation in this slice, and out-of-scope workflows before invocation.

**Alternatives considered**: Names such as `watermarks.set`, `set_watermark`, or `youtube_watermarks_set` were rejected by YT-201/YT-202 naming rules because Layer 2 public names use `resource_method` and the repository context already identifies YouTube. Hiding quota or media requirements in implementation-only docs was rejected because caller-visible tools must show access, quota, and mutation impact before invocation.

## Decision: Input contract

**Rationale**: The local Layer 1 wrapper for YT-154 requires exactly one target channel `channelId`, a `body` mapping with watermark timing and position metadata, and a `media` upload descriptor with `mimeType` and `content`. The public MCP contract should therefore accept one object with required `channelId`, `body`, and `media`; it should reject missing, blank, non-string, incomplete, ambiguous, unsupported, metadata-only, media-only, delegated, or extra fields before endpoint execution where locally detectable.

**Alternatives considered**: Accepting aliases such as `channel` or `targetChannel` was rejected because Layer 2 stays close to the Layer 1 endpoint contract. Accepting arbitrary body fields without validation was rejected because callers need deterministic feedback for watermark metadata errors. Accepting `onBehalfOfContentOwner` was rejected for this slice because the local Layer 1 dependency explicitly leaves that behavior outside the guaranteed boundary.

## Decision: Media upload boundary

**Rationale**: The public contract should keep the Layer 1 upload boundary visible: media requires `mimeType` and `content`, accepted MIME types are `image/jpeg`, `image/png`, and `application/octet-stream`, and content must remain within the documented 10 MB watermark limit when determinable locally. Public results and errors should expose only safe upload descriptors such as MIME type, content-present state, and size category, never raw media content.

**Alternatives considered**: Accepting raw bytes in public examples was rejected because examples and docs must not expose private media. Supporting additional MIME types was rejected unless Layer 1 and tests deliberately expand the supported boundary.

## Decision: Sparse watermark-update acknowledgment semantics

**Rationale**: Successful `watermarks.set` behavior can be sparse and does not require a refreshed channel branding resource. The public result should therefore be a structured mutation or upload acknowledgment that preserves endpoint identity, quota context, safe access context, target channel identity, watermark metadata context, safe media upload context, and availability state without fabricating channel branding metadata, watermark lookup results, media hosting URLs, analytics, recommendations, summaries, or policy outcomes.

**Alternatives considered**: Returning a full channel branding resource was rejected because the endpoint does not promise one. Returning only a boolean was rejected because callers need request, quota, auth, endpoint, target, metadata, and upload context for auditability and downstream workflow composition.

## Decision: OAuth-only access

**Rationale**: The YT-154 Layer 1 wrapper enforces OAuth-required access, and YT-254 requires OAuth expectations to be documented clearly. Missing OAuth should be categorized as `authentication_failed`; present but insufficient OAuth should be `authorization_failed` or the closest shared safe category. API-key-only access must not be presented as valid.

**Alternatives considered**: Mixed API-key/OAuth behavior was rejected because watermark setting is an authorized channel branding action. Treating missing OAuth as a generic validation failure was rejected because callers need to distinguish malformed inputs from missing credentials.

## Decision: Result shape

**Rationale**: The Layer 2 result should be a structured watermark-update acknowledgment that preserves `endpoint`, `quotaCost`, safe target channel context, safe watermark metadata context, safe upload context, safe access context, availability, update status, and mutation details while remaining near-raw enough for endpoint-backed callers.

**Alternatives considered**: Returning refreshed channel metadata, a watermark lookup object, a media hosting URL, or an automated branding state machine was rejected because those are not returned by the endpoint. Returning raw sparse content was rejected because callers need a machine-readable acknowledgment to compose workflows safely.

## Decision: Error categories and safety

**Rationale**: Validation and upstream failures should use shared safe categories: `invalid_request`, `authentication_failed`, `authorization_failed`, `quota_exhausted`, `resource_not_found`, `unsupported_upload`, `endpoint_unavailable`, `deprecated_endpoint`, and `upstream_failure`. General authorization, quota, invalid request, unsupported media, upload, policy, forbidden, not-found, conflict, and availability errors can occur. Error details must be sanitized to remove API keys, OAuth tokens, authorization headers, raw media content, raw upstream bodies, stack traces, raw request context, and secret-bearing details.

**Alternatives considered**: Returning raw upstream or upload errors was rejected because MCP-facing tools require safe, deterministic error output. Creating endpoint-specific public categories for every possible upstream detail was rejected because shared Layer 2 conventions already provide stable categories for callers.

## Decision: Verification strategy

**Rationale**: Focused verification should cover public metadata and examples, `channelId` validation, `body` validation, `media` validation, OAuth enforcement, sparse acknowledgment mapping, safe upstream error mapping, exports, default catalog inclusion, and dispatcher execution. Final completion requires the full repository command `pytest` and quality command `ruff check .`. Every new or changed Python function must include a reStructuredText docstring documenting purpose, parameters, return values, raised errors, and side effects where relevant.

**Alternatives considered**: Running only watermarks-focused checks was rejected by the constitution because full-suite validation is required after final changes. Skipping Python docstring planning was rejected because the constitution requires reStructuredText docstrings for all new or changed Python functions.

## Decision: Scope boundary

**Rationale**: YT-254 exposes only the low-level `watermarks.set` endpoint as `watermarks_set`. Watermark removal belongs to `watermarks_unset`; channel lookup and channel updates belong to channel tools; banner upload belongs to `channelBanners_insert`; thumbnail upload belongs to `thumbnails_set`; video, caption, playlist, comment, transcript, analytics, recommendations, ranking, summarization, enrichment, automated branding, and cross-endpoint workflows remain out of scope.

**Alternatives considered**: Expanding into channel branding management, watermark discovery, watermark removal, media transformation, or research workflow was rejected because Layer 2 tools are endpoint-backed and near-raw. Higher-level orchestration belongs to Layer 3 or separate endpoint slices.

## Sources

- Local feature specification: `/Users/ctgunn/Projects/youtube-mcp-server/specs/254-watermarks-set/spec.md`
- Local seed slice: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`
- Local PRD: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/PRD.md`
- Local Layer 1 wrapper: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/watermarks.py`
- Local Layer 1 validator: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/validators/watermarks.py`
- Local Layer 1 wrapper tests: `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- Local Layer 2 upload mutation patterns: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/thumbnails.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`
- Local dispatcher and catalog surfaces: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`

## Clarification Closure

All planning-time clarifications for YT-254 are resolved in this research artifact. No open clarification markers remain.
