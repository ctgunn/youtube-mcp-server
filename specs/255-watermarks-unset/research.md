# Research: Layer 2 Tool `watermarks_unset`

## Decision: Extend the existing Python Layer 2 watermarks module

**Rationale**: The local Layer 2 package already contains `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py` for `watermarks_set`. Adding `watermarks_unset` there keeps endpoint-backed `watermarks.*` tools cohesive and lets the feature reuse shared Layer 2 contract primitives, response boundaries, safe error handling, examples, public exports, and default dispatcher registration patterns.

**Alternatives considered**: Creating a second watermark module was rejected because it would split one upstream resource family. Adding unset behavior to thumbnails, channel banners, channels, or videos was rejected because this is a distinct upstream `watermarks` resource. Creating a higher-level branding module was rejected because YT-255 is a low-level Layer 2 endpoint tool.

## Decision: Reuse YT-155 `build_watermarks_unset_wrapper()`

**Rationale**: The local Layer 1 dependency already exposes `watermarks.unset` with operation key `watermarks.unset`, `POST /youtube/v3/watermarks/unset`, quota cost `50`, OAuth-required access, required `channelId`, rejected `body` and `media` payloads, rejected unsupported top-level fields, rejected partner-only delegation in this slice, and normalized watermark-removal acknowledgment support. YT-255 should expose that capability publicly through Layer 2 without redefining upstream execution, auth, quota, or base validation behavior.

**Alternatives considered**: Reimplementing upstream request construction in Layer 2 was rejected because it would duplicate Layer 1 behavior. Expanding Layer 1 to include partner delegation is out of scope unless implementation reveals a deliberately approved narrow contract expansion.

## Decision: Public identity and metadata

**Rationale**: The public tool must be named `watermarks_unset`, mapped to upstream resource `watermarks` and method `unset`, and show operation key `watermarks.unset`. Discovery metadata, descriptions, usage notes, and examples must expose quota cost `50`, OAuth-only access, required `channelId`, no-upload behavior, sparse acknowledgment semantics, rejected partner delegation in this slice, no-removal-possible caveats, and out-of-scope workflows before invocation.

**Alternatives considered**: Names such as `watermarks.unset`, `unset_watermark`, or `youtube_watermarks_unset` were rejected by YT-201/YT-202 naming rules because Layer 2 public names use `resource_method` and the repository context already identifies YouTube. Hiding quota or no-upload requirements in implementation-only docs was rejected because caller-visible tools must show access, quota, and mutation impact before invocation.

## Decision: Input contract

**Rationale**: The local Layer 1 wrapper for YT-155 requires exactly one target channel `channelId` and rejects watermark setting payloads. The public MCP contract should therefore accept one object with required `channelId`; reject missing, blank, non-string, ambiguous, unsupported, delegated, upload-oriented, metadata-oriented, bulk, alias-only, or extra fields before endpoint execution where locally detectable; and keep any OAuth authorization context outside caller-visible request fields.

**Alternatives considered**: Accepting aliases such as `channel` or `targetChannel` was rejected because Layer 2 stays close to the Layer 1 endpoint contract. Silently ignoring `body` or `media` was rejected because it hides caller mistakes and blurs unset with set. Accepting `onBehalfOfContentOwner` was rejected for this slice because the local Layer 1 dependency explicitly leaves partner delegation outside the guaranteed boundary.

## Decision: No-upload boundary

**Rationale**: The public contract should make clear that `watermarks_unset` removes a watermark without accepting image content, watermark placement metadata, display metadata, upload descriptors, or media-only request shapes. Safe results and errors should not echo raw media or metadata if a caller mistakenly supplies them.

**Alternatives considered**: Reusing `watermarks_set` upload validation was rejected because unset has no media upload. Ignoring supplied upload or metadata payloads was rejected because deterministic validation is required for automation and would otherwise make unsupported input look accepted.

## Decision: Sparse watermark-removal acknowledgment semantics

**Rationale**: Successful `watermarks.unset` behavior can be sparse and does not require a refreshed channel branding resource. The public result should therefore be a structured mutation acknowledgment that preserves endpoint identity, quota context, safe access context, target channel context, availability state, and no-upload context without fabricating channel branding metadata, watermark lookup results, media hosting URLs, analytics, recommendations, summaries, or policy outcomes.

**Alternatives considered**: Returning a full channel branding resource was rejected because the endpoint does not promise one. Returning only a boolean was rejected because callers need request, quota, auth, endpoint, target, and acknowledgment context for auditability and downstream workflow composition.

## Decision: OAuth-only access

**Rationale**: The YT-155 Layer 1 wrapper enforces OAuth-required access, and YT-255 requires OAuth expectations to be documented clearly. Missing OAuth should be categorized as `authentication_failed`; present but insufficient OAuth should be `authorization_failed` or the closest shared safe category. API-key-only access must not be presented as valid.

**Alternatives considered**: Mixed API-key/OAuth behavior was rejected because watermark removal is an authorized channel branding action. Treating missing OAuth as a generic validation failure was rejected because callers need to distinguish malformed inputs from missing credentials.

## Decision: Result shape

**Rationale**: The Layer 2 result should be a structured watermark-removal acknowledgment that preserves `endpoint`, `sourceOperation`, `quotaCost`, safe target channel context, safe access context, no-upload context, availability, removal status, and mutation details while remaining near-raw enough for endpoint-backed callers.

**Alternatives considered**: Returning refreshed channel metadata, a watermark lookup object, a media hosting URL, or an automated branding state machine was rejected because those are not returned by the endpoint. Returning raw sparse content was rejected because callers need a machine-readable acknowledgment to compose workflows safely.

## Decision: Error categories and safety

**Rationale**: Validation and upstream failures should use shared safe categories: `invalid_request`, `authentication_failed`, `authorization_failed`, `quota_exhausted`, `target_channel_failed`, `no_removal_possible`, `endpoint_unavailable`, `deprecated_endpoint`, `conflict`, `upstream_refused`, and `upstream_failure`. Error details must be sanitized to remove API keys, OAuth tokens, authorization headers, raw media content, raw upstream bodies, stack traces, raw request context, and secret-bearing details.

**Alternatives considered**: Returning raw upstream errors was rejected because MCP-facing tools require safe, deterministic error output. Creating endpoint-specific public categories for every possible upstream detail was rejected because shared Layer 2 conventions already provide stable categories for callers.

## Decision: Replace the representative placeholder catalog entry with the concrete contract

**Rationale**: The shared representative catalog currently lists `watermarks_unset` through a placeholder-style contract. Once YT-255 adds the concrete tool contract, the catalog should use `build_watermarks_unset_contract()` so discovery and representative examples do not drift from executable behavior.

**Alternatives considered**: Keeping the placeholder alongside the concrete contract was rejected because it risks duplicate or conflicting catalog metadata. Removing catalog coverage was rejected because the Layer 2 catalog is part of caller-facing discovery.

## Decision: Verification strategy

**Rationale**: Focused verification should cover public metadata and examples, `channelId` validation, no-upload validation, OAuth enforcement, sparse acknowledgment mapping, no-removal-possible mapping, safe upstream error mapping, exports, default catalog inclusion, and dispatcher execution. Final completion requires the full repository command `pytest` and quality command `ruff check .`. Every new or changed Python function must include a reStructuredText docstring documenting purpose, parameters, return values, raised errors, and side effects where relevant.

**Alternatives considered**: Running only watermarks-focused checks was rejected by the constitution because full-suite validation is required after final changes. Skipping Python docstring planning was rejected because the constitution requires reStructuredText docstrings for all new or changed Python functions.

## Decision: Scope boundary

**Rationale**: YT-255 exposes only the low-level `watermarks.unset` endpoint as `watermarks_unset`. Watermark upload belongs to `watermarks_set`; channel lookup and channel updates belong to channel tools; banner upload belongs to `channelBanners_insert`; thumbnail upload belongs to `thumbnails_set`; video, caption, playlist, comment, transcript, analytics, recommendations, ranking, summarization, enrichment, automated branding, and cross-endpoint workflows remain out of scope.

**Alternatives considered**: Expanding into channel branding management, watermark discovery, watermark upload, media transformation, or research workflow was rejected because Layer 2 tools are endpoint-backed and near-raw. Higher-level orchestration belongs to Layer 3 or separate endpoint slices.

## Sources

- Local feature specification: `/Users/ctgunn/Projects/youtube-mcp-server/specs/255-watermarks-unset/spec.md`
- Local seed slice: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`
- Local PRD: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/PRD.md`
- Local Layer 1 wrapper: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/watermarks.py`
- Local Layer 1 validator: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/validators/watermarks.py`
- Local Layer 1 wrapper tests: `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- Local Layer 2 watermarks module: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- Local Layer 2 mutation patterns: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- Local dispatcher and catalog surfaces: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`

## Clarification Closure

All planning-time clarifications for YT-255 are resolved in this research artifact. No open clarification markers remain.
