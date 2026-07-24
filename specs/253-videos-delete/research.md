# Research: Layer 2 Tool `videos_delete`

## Decision: Use the existing Python Layer 2 videos module

**Rationale**: The local Layer 2 videos family already lives at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py` and currently contains `videos_list`, `videos_insert`, `videos_update`, `videos_rate`, `videos_getRating`, and `videos_reportAbuse`. Adding `videos_delete` there keeps endpoint-backed `videos.*` tools cohesive and lets the feature reuse shared Layer 2 contract primitives, response boundaries, safe error handling, examples, public exports, and default dispatcher registration patterns.

**Alternatives considered**: Creating a separate deletion module was rejected because the public tool is a single `videos` resource-family endpoint. Adding the behavior to search, captions, thumbnails, playlist, analytics, recommendation, or higher-level content-management modules was rejected because YT-253 is a low-level Layer 2 endpoint tool.

## Decision: Reuse YT-153 `build_videos_delete_wrapper()`

**Rationale**: The local Layer 1 dependency already exposes `videos.delete` with operation key `videos.delete`, `DELETE /youtube/v3/videos`, quota cost `50`, OAuth-required access, required `id`, no request body, rejected `onBehalfOfContentOwner` in this slice, and normalized no-content deletion acknowledgment support. YT-253 should expose that capability publicly through Layer 2 without redefining upstream execution, auth, quota, or base validation behavior.

**Alternatives considered**: Reimplementing upstream request construction in Layer 2 was rejected because it would duplicate Layer 1 behavior. Expanding Layer 1 to include `onBehalfOfContentOwner` is out of scope unless implementation reveals a deliberately approved narrow contract expansion.

## Decision: Public identity and metadata

**Rationale**: The public tool must be named `videos_delete`, mapped to upstream resource `videos` and method `delete`, and show operation key `videos.delete`. Discovery metadata, descriptions, usage notes, and examples must expose quota cost `50`, OAuth-only access, required `id`, no-body request semantics, destructive-action guidance, no-content acknowledgment semantics, rejected partner delegation in this slice, and out-of-scope workflows before invocation.

**Alternatives considered**: Names such as `videos.delete`, `delete_video`, or `youtube_videos_delete` were rejected by YT-201/YT-202 naming rules because Layer 2 public names use `resource_method` and the repository context already identifies YouTube. Hiding quota or destructive-action semantics in implementation-only docs was rejected because caller-visible tools must show access, quota, and mutation impact before invocation.

## Decision: Input contract

**Rationale**: The local Layer 1 wrapper for YT-153 requires exactly one target video `id`, sends no request body, and rejects delegated `onBehalfOfContentOwner` behavior in this slice. The public MCP contract should therefore accept one object with required `id`; it should reject missing, blank, non-string, ambiguous, duplicate, comma-separated, unsupported, or extra fields before endpoint execution where locally detectable.

**Alternatives considered**: Accepting a request `body` was rejected because the Layer 1 contract and endpoint delete semantics use query-style target identity and no body. Accepting top-level aliases such as `videoId` was rejected because Layer 2 stays close to the Layer 1 endpoint contract. Accepting `onBehalfOfContentOwner` was rejected for this slice because the local Layer 1 dependency explicitly leaves that behavior outside the guaranteed boundary. Accepting arbitrary modifiers or bulk delete fields was rejected because deletion semantics are destructive and must not be silently changed.

## Decision: No-content deletion acknowledgment semantics

**Rationale**: Successful `videos.delete` behavior returns no refreshed video resource. The public result should therefore be a structured mutation acknowledgment that preserves endpoint identity, quota context, safe access context, target video identity, destructive-action context, and availability state without fabricating video metadata, recovery state, analytics, recommendations, summaries, or policy outcomes.

**Alternatives considered**: Returning a full video resource was rejected because the upstream operation does not return one. Returning only a boolean was rejected because callers need request, quota, auth, endpoint, and target context for auditability and downstream workflow composition.

## Decision: OAuth-only access

**Rationale**: The YT-153 Layer 1 wrapper enforces OAuth-required access, and YT-253 requires OAuth expectations to be documented clearly. Missing OAuth should be categorized as `authentication_failed`; present but insufficient OAuth should be `authorization_failed` or the closest shared safe category. API-key-only access must not be presented as valid.

**Alternatives considered**: Mixed API-key/OAuth behavior was rejected because deletion is an authorized user action. Treating missing OAuth as a generic validation failure was rejected because callers need to distinguish malformed inputs from missing credentials.

## Decision: Result shape

**Rationale**: The Layer 2 result should be a structured deletion acknowledgment that preserves `endpoint`, `quotaCost`, safe target context, safe access context, availability, deletion status, and mutation details while remaining near-raw enough for endpoint-backed callers.

**Alternatives considered**: Returning refreshed metadata, a recovery object, or a content-management state machine was rejected because those are not returned by the endpoint. Returning raw empty content was rejected because callers need a machine-readable acknowledgment to compose workflows safely.

## Decision: Error categories and safety

**Rationale**: Validation and upstream failures should use shared safe categories: `invalid_request`, `authentication_failed`, `authorization_failed`, `quota_exhausted`, `resource_not_found`, `endpoint_unavailable`, `deprecated_endpoint`, and `upstream_failure`. General authorization, quota, invalid request, policy, forbidden, not-found, conflict, and availability errors can occur. Error details must be sanitized to remove API keys, OAuth tokens, authorization headers, raw upstream bodies, stack traces, raw request context, and secret-bearing details.

**Alternatives considered**: Returning raw upstream errors was rejected because MCP-facing tools require safe, deterministic error output. Creating endpoint-specific public categories for every possible upstream detail was rejected because shared Layer 2 conventions already provide stable categories for callers.

## Decision: Verification strategy

**Rationale**: Focused verification should cover public metadata and examples, `id` validation, OAuth enforcement, no-content acknowledgment mapping, safe upstream error mapping, exports, default catalog inclusion, and dispatcher execution. Final completion requires the full repository command `pytest` and quality command `ruff check .`. Every new or changed Python function must include a reStructuredText docstring documenting purpose, parameters, return values, raised errors, and side effects where relevant.

**Alternatives considered**: Running only videos-focused checks was rejected by the constitution because full-suite validation is required after final changes. Skipping Python docstring planning was rejected because the constitution requires reStructuredText docstrings for all new or changed Python functions.

## Decision: Scope boundary

**Rationale**: YT-253 exposes only the low-level `videos.delete` endpoint as `videos_delete`. Listing belongs to `videos_list`; rating mutation belongs to `videos_rate`; rating lookup belongs to `videos_getRating`; abuse reporting belongs to `videos_reportAbuse`; metadata update and upload belong to separate video tools; captions, thumbnails, playlists, comments, transcripts, analytics, recommendations, ranking, summarization, enrichment, recovery, policy review, and cross-endpoint workflows remain out of scope.

**Alternatives considered**: Expanding into content management, recovery, metadata lookup, or moderation workflow was rejected because Layer 2 tools are endpoint-backed and near-raw. Higher-level orchestration belongs to Layer 3 or separate endpoint slices.

## Sources

- Local feature specification: `/Users/ctgunn/Projects/youtube-mcp-server/specs/253-videos-delete/spec.md`
- Local seed slice: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`
- Local PRD: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/PRD.md`
- Local Layer 1 wrapper: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/videos.py`
- Local Layer 1 wrapper tests: `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- Local Layer 2 videos family: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- Local destructive delete patterns: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`

## Clarification Closure

All planning-time clarifications for YT-253 are resolved in this research artifact. No open clarification markers remain.
