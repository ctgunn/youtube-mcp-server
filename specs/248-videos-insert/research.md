# Research: Layer 2 Tool `videos_insert`

## Decision: Use the existing Python Layer 2 videos module

**Rationale**: YT-247 established `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py` as the Layer 2 videos resource-family module. Adding `videos_insert` there keeps `videos.list` and `videos.insert` cohesive under the upstream `videos` resource and allows the feature to reuse shared Layer 2 contract primitives, response-boundary helpers, safe error sanitation, public exports, examples, and default dispatcher registration patterns.

**Alternatives considered**: Creating a separate upload module was rejected because the public tool name and resource family are videos-specific. Adding this to captions, thumbnails, playlists, search, or a higher-level publishing module was rejected because the feature is a single low-level endpoint-backed tool.

## Decision: Reuse YT-148 `build_videos_insert_wrapper()`

**Rationale**: The local Layer 1 dependency already exposes `videos.insert` with operation key `videos.insert`, `POST /youtube/v3/videos`, quota cost `1600`, OAuth-required access, required `part`, `body`, and `media`, optional `uploadMode`, `notifySubscribers`, and `onBehalfOfContentOwner`, supported upload modes `multipart` and `resumable`, and an audit/private-default caveat. YT-248 should expose that capability publicly through Layer 2 without redefining another upstream contract.

**Alternatives considered**: Reimplementing upstream request construction in Layer 2 was rejected because it would duplicate Layer 1 execution, auth, quota, validation, and error behavior. Changing Layer 1 is outside this slice unless a narrow missing export or metadata gap blocks the public tool.

## Decision: Public identity and metadata

**Rationale**: The public tool must be named `videos_insert`, mapped to upstream resource `videos` and method `insert`, and show operation key `videos.insert`. Discovery metadata, descriptions, usage notes, and examples must expose quota cost `1600`, OAuth-only access, media-upload requirements, media-constrained or limited availability, and the created-video response boundary before invocation.

**Alternatives considered**: A generic `youtube_videos_insert` name was rejected by YT-201/YT-202 naming rules. Hiding quota cost in implementation-only docs was rejected because high-cost operations require public pre-invocation disclosure.

## Decision: Input contract

**Rationale**: The Layer 2 input schema should accept one object with required `part`, `body`, and `media`, and optional `uploadMode`, `notifySubscribers`, and `onBehalfOfContentOwner` where supported. `part` must be non-empty, `body` must be a metadata object, `media` must be a media descriptor object, `uploadMode` must be absent or one of `multipart` and `resumable`, `notifySubscribers` must be boolean when supplied, and delegation must require eligible OAuth context.

**Alternatives considered**: Supporting arbitrary upstream parameters was rejected to keep the public contract testable and safe. Making media optional was rejected because YT-248 and YT-148 both define video creation as media-upload-oriented. Accepting raw media content in public examples was rejected because public docs and errors must not expose raw media payloads.

## Decision: OAuth-only access

**Rationale**: Video creation requires eligible OAuth authorization for every supported request. Missing OAuth should be categorized as `authentication_failed`; present but insufficient OAuth should be `authorization_failed`. API-key-only access must not be presented as a valid creation path.

**Alternatives considered**: Mixed API-key/OAuth behavior was rejected because that applies to read selectors such as `videos_list`, not to `videos.insert`. Treating missing OAuth as a validation failure was rejected because callers need to distinguish malformed input from missing credentials.

## Decision: Result shape

**Rationale**: Successful calls should return an upload result containing `endpoint`, `quotaCost`, `requestedParts`, `upload`, `auth`, `availability`, optional safe delegation context, `item` or equivalent created video resource payload, and returned upstream fields. The result must preserve endpoint-backed video fields without fabricating publication state, processing state, thumbnails, captions, playlists, analytics, recommendations, rankings, summaries, or enrichment.

**Alternatives considered**: Returning a list result was rejected because `videos.insert` creates one video resource. Returning only an acknowledgment was rejected because the upstream creation response may include a video resource that should remain available to callers.

## Decision: Error categories and safety

**Rationale**: Validation and upstream failures should use shared safe categories: `invalid_request`, `authentication_failed`, `authorization_failed`, `quota_exhausted`, `resource_not_found` where applicable, `endpoint_unavailable`, `deprecated_endpoint`, and `upstream_failure`. Error details must be sanitized to remove API keys, OAuth tokens, authorization headers, raw media payloads, signed URLs, raw upstream bodies, stack traces, and secret-bearing details.

**Alternatives considered**: Returning raw upstream errors was rejected because MCP-facing tools must provide safe, deterministic error messaging. Creating endpoint-specific ad hoc categories was rejected unless the nearest shared category cannot express an upstream outcome.

## Decision: Availability and caveats

**Rationale**: `videos_insert` should surface media-constrained or limited availability because video upload can be affected by release policy, audit, channel ownership, or private-default behavior. The public contract should make those caveats visible without turning this feature into an account review, publishing workflow, or visibility management tool.

**Alternatives considered**: Marking the tool simply `active` was rejected as too weak for upload-sensitive behavior. Blocking the feature until every production release policy is known was rejected because the contract can expose caveats and categorize availability refusals safely.

## Decision: Verification strategy

**Rationale**: Focused verification should cover `tests/contract/test_youtube_videos_contract.py`, `tests/unit/test_youtube_videos.py`, `tests/integration/test_youtube_videos_registration.py`, shared contract/catalog tests, shared scaffolding tests, and default tool-registration tests. Final completion requires `pytest` and `ruff check .`. Every new or changed Python function must include a reStructuredText docstring.

**Alternatives considered**: Running only videos-focused tests was rejected by the constitution because full-suite validation is required after final code changes. Skipping docstring planning was rejected because the constitution explicitly requires reStructuredText docstrings for new and changed Python functions.

## Decision: Scope boundary

**Rationale**: YT-248 exposes only the low-level `videos.insert` endpoint as `videos_insert`. Automatic publishing, post-upload editing, thumbnails, captions, playlists, comments, ratings, transcripts, analytics, recommendations, ranking, summarization, enrichment, and cross-endpoint workflows remain out of scope.

**Alternatives considered**: Expanding the tool into a full video publishing workflow was rejected because Layer 2 tools are endpoint-backed and near-raw. Higher-level orchestration belongs to Layer 3 or separate endpoint slices.
