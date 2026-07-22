# Research: Layer 2 Tool `videos_update`

## Decision: Use the existing Python Layer 2 videos module

**Rationale**: YT-247 and YT-248 established `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py` as the Layer 2 videos resource-family module. Adding `videos_update` there keeps `videos.list`, `videos.insert`, and `videos.update` cohesive under the upstream `videos` resource and allows the feature to reuse shared Layer 2 contract primitives, response-boundary helpers, safe error sanitation, public exports, examples, and default dispatcher registration patterns.

**Alternatives considered**: Creating a separate mutation module was rejected because the public tool name and resource family are videos-specific. Adding this to captions, thumbnails, playlists, search, or a higher-level publishing module was rejected because the feature is a single low-level endpoint-backed tool.

## Decision: Reuse YT-149 `build_videos_update_wrapper()`

**Rationale**: The local Layer 1 dependency already exposes `videos.update` with operation key `videos.update`, `PUT /youtube/v3/videos`, quota cost `50`, OAuth-required access, required `part` and `body`, and current validation for `part=snippet`, `body.id`, and `body.snippet.title`. YT-249 should expose that capability publicly through Layer 2 without redefining another upstream contract.

**Alternatives considered**: Reimplementing upstream request construction in Layer 2 was rejected because it would duplicate Layer 1 execution, auth, quota, validation, and error behavior. Expanding Layer 1 writable fields is outside this slice unless a narrow missing export or metadata gap blocks the public tool.

## Decision: Public identity and metadata

**Rationale**: The public tool must be named `videos_update`, mapped to upstream resource `videos` and method `update`, and show operation key `videos.update`. Discovery metadata, descriptions, usage notes, and examples must expose quota cost `50`, OAuth-only access, writable-part requirements, update body expectations, replacement-oriented caveats for included parts, and the updated-video response boundary before invocation.

**Alternatives considered**: A generic `youtube_videos_update` name was rejected by YT-201/YT-202 naming rules. Hiding quota cost or update semantics in implementation-only docs was rejected because mutation operations require public pre-invocation disclosure.

## Decision: Input contract

**Rationale**: The Layer 2 input schema should accept one object with required `part` and `body`, and optional `onBehalfOfContentOwner` where supported. The current local Layer 1 wrapper supports `part=snippet`, requires `body.id` for the target video, and requires `body.snippet.title` for the minimum writable update path. Unsupported top-level fields, unsupported body fields, unsupported snippet fields, read-only fields, missing identity, and body/part mismatches should be rejected before endpoint execution.

**Alternatives considered**: Supporting arbitrary upstream fields was rejected to keep the public contract testable and safe. Treating media upload as part of update was rejected because `videos.update` updates resource metadata and does not replace media content. Allowing broad status, localizations, tags, or description updates was rejected until the Layer 1 contract deliberately expands those writable fields.

## Decision: OAuth-only access

**Rationale**: Video updates require eligible OAuth authorization for every supported request. Missing OAuth should be categorized as `authentication_failed`; present but insufficient OAuth should be `authorization_failed` or the closest shared safe category. API-key-only access must not be presented as a valid update path.

**Alternatives considered**: Mixed API-key/OAuth behavior was rejected because that applies to read selectors such as `videos_list`, not to `videos.update`. Treating missing OAuth as a validation failure was rejected because callers need to distinguish malformed input from missing credentials.

## Decision: Result shape

**Rationale**: Successful calls should return a mutation result containing `endpoint`, `quotaCost`, `requestedParts`, `update`, `auth`, optional safe delegation context, `item` or equivalent updated video resource payload, and returned upstream fields. The result must preserve endpoint-backed video fields without fabricating media state, publication workflow state, thumbnails, captions, playlists, analytics, recommendations, rankings, summaries, transcript text, or enrichment.

**Alternatives considered**: Returning a list result was rejected because `videos.update` mutates one video resource. Returning only an acknowledgment was rejected because the upstream update response may include a video resource that should remain available to callers.

## Decision: Error categories and safety

**Rationale**: Validation and upstream failures should use shared safe categories: `invalid_request`, `authentication_failed`, `authorization_failed`, `quota_exhausted`, `resource_not_found`, `endpoint_unavailable`, `deprecated_endpoint`, and `upstream_failure`. Error details must be sanitized to remove API keys, OAuth tokens, authorization headers, raw upstream bodies, stack traces, raw request context, and secret-bearing details.

**Alternatives considered**: Returning raw upstream errors was rejected because MCP-facing tools must provide safe, deterministic error messaging. Creating endpoint-specific ad hoc categories was rejected unless the nearest shared category cannot express an upstream outcome.

## Decision: Verification strategy

**Rationale**: Focused verification should cover `tests/contract/test_youtube_videos_contract.py`, `tests/unit/test_youtube_videos.py`, `tests/integration/test_youtube_videos_registration.py`, shared contract/catalog tests, shared scaffolding tests, and default tool-registration tests. Final completion requires `pytest` and `ruff check .`. Every new or changed Python function must include a reStructuredText docstring.

**Alternatives considered**: Running only videos-focused tests was rejected by the constitution because full-suite validation is required after final code changes. Skipping docstring planning was rejected because the constitution explicitly requires reStructuredText docstrings for new and changed Python functions.

## Decision: Scope boundary

**Rationale**: YT-249 exposes only the low-level `videos.update` endpoint as `videos_update`. Media upload, media replacement, transcoding, automatic publishing workflow, video creation, deletion, rating mutation, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendations, ranking, summarization, enrichment, and cross-endpoint workflows remain out of scope.

**Alternatives considered**: Expanding the tool into a full video publishing or editing workflow was rejected because Layer 2 tools are endpoint-backed and near-raw. Higher-level orchestration belongs to Layer 3 or separate endpoint slices.
