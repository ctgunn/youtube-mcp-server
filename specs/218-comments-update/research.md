# Research: Layer 2 Tool `comments_update`

## Decision: Expose `comments_update` as a low-level comment editing tool

**Rationale**: The seed slice YT-218 requires a Layer 2 tool named `comments_update` that maps directly to YouTube `comments.update`. The official comments resource reference describes `update` as modifying a comment, while separate methods own listing, insertion, deletion, and moderation behavior.

**Alternatives considered**:

- Build a higher-level comment editing workflow with generated rewrites or moderation decisions: rejected because Layer 2 tools must remain near-direct endpoint-backed operations.
- Combine update and moderation behavior in one tool: rejected because `comments.setModerationStatus` is a separate seed slice and upstream method.
- Add comment listing or preflight lookup into this tool: rejected because that would introduce cross-endpoint behavior outside the low-level Layer 2 contract.

## Decision: Require OAuth and expose quota cost 50 everywhere

**Rationale**: Official YouTube API guidance requires authorization tokens for insert, update, and delete requests. The official quota table lists `comments.update` at 50 units. The Layer 1 YT-118 wrapper also marks the endpoint as `oauth_required` and quota cost 50. The public contract must show this in metadata, description, usage notes, and examples before invocation.

**Alternatives considered**:

- Allow API-key-only access: rejected because comment updates are write operations requiring eligible OAuth authorization.
- Hide quota in implementation-only metadata: rejected by YT-202 and the constitution's contract-first requirement.
- Treat locally invalid requests as quota-bearing in examples: rejected because local validation should prevent unsupported requests from being sent upstream, while still documenting the official cost of actual endpoint calls.

## Decision: Require `part` with `snippet`, `body.id`, and `body.snippet.textOriginal`

**Rationale**: Official `comments.update` documentation says `part` is required, that `snippet` must be included because it contains all updateable properties, and that the request body can set `snippet.textOriginal`. The successful response is a comment resource. The local YT-118 Layer 1 wrapper uses `body.id` plus `body.snippet.textOriginal` as the deterministic update shape, so Layer 2 should preserve that boundary for public callers.

**Alternatives considered**:

- Permit metadata-only updates: rejected because the endpoint updates comment text through a request body.
- Permit parent relationship or moderation status changes: rejected because those fields are not the writable update field for this slice.
- Permit opaque pass-through bodies for forward compatibility: rejected because this project validates endpoint-specific request shapes before execution.

## Decision: Return a near-raw updated comment resource result

**Rationale**: Official documentation returns a comment resource when `comments.update` succeeds. Existing Layer 2 mutation tools return light wrapper context such as endpoint, quota cost, requested parts, mutation status, and item while preserving returned upstream fields.

**Alternatives considered**:

- Return only an acknowledgment: rejected because the endpoint returns a comment resource and callers need the updated comment identity and fields.
- Enrich with parent thread/channel/video metadata: rejected because this would cross endpoint boundaries and violate Layer 2 scope.
- Present updates as a collection: rejected because `comments.update` returns one resource.

## Decision: Reuse the existing comments family module and tests

**Rationale**: YT-216 introduced `src/mcp_server/tools/youtube_common/comments.py` and matching comments contract/unit/integration tests; YT-217 extended the same module for `comments_insert`. Extending that module keeps related `comments_*` tools together and follows the resource-family pattern used by captions, channels, and channel sections.

**Alternatives considered**:

- Create a separate `comments_update.py`: rejected because it would split one resource family across files prematurely and duplicate registration/export patterns.
- Put the tool in generic shared contracts: rejected because endpoint-specific validation, examples, writable-field caveats, and update result mapping belong to the concrete comments family.

## Decision: Map validation and upstream failures to shared safe Layer 2 categories

**Rationale**: YT-201/YT-202 shared contracts and existing comments tools use safe public categories such as `invalid_request`, `authentication_failed`, `authorization_failed`, `quota_exhausted`, `resource_not_found`, `endpoint_unavailable`, `deprecated_endpoint`, and `upstream_failure`. Official update errors include `commentTextTooLong`, `invalidCommentMetadata`, `operationNotSupported`, `processingFailure`, `forbidden`, `ineligibleAccount`, and `commentNotFound`; these map naturally to shared categories without exposing raw upstream diagnostics.

**Alternatives considered**:

- Preserve raw upstream error detail names only: rejected because public MCP clients need stable shared categories and safe diagnostics.
- Collapse every update failure into `upstream_failure`: rejected because callers need to distinguish validation, authorization, quota, and missing target-comment outcomes.
- Add a new custom error taxonomy for comments update: rejected because YT-201 requires shared conventions across Layer 2 tools.

## Decision: Follow Red-Green-Refactor with focused contract, unit, integration, full-suite, and lint evidence

**Rationale**: The constitution makes Red-Green-Refactor non-negotiable and requires full repository test-suite execution after final code changes. The implementation should begin with failing tests for discovery, schema, validation, handler behavior, result mapping, error mapping, examples, exports, and default registry integration.

**Alternatives considered**:

- Implementing first and adding tests afterward: rejected by the constitution.
- Running only focused tests: rejected because full-suite validation is required before completion.
- Omitting docstring work from planning: rejected because every new or changed Python function must have a reStructuredText docstring.

## Decision: No unresolved clarifications remain

**Rationale**: The seed, feature spec, constitution, current codebase, existing YT-118 wrapper, existing comments Layer 2 tools, and official documentation resolve the endpoint identity, quota, auth mode, required fields, response shape, dependencies, and validation boundaries.

**Alternatives considered**:

- Ask for additional scope confirmation: rejected because the feature description explicitly names YT-218 and the seed provides enough scope detail.

## Sources

- Local seed: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`
- Local feature spec: `/Users/ctgunn/Projects/youtube-mcp-server/specs/218-comments-update/spec.md`
- Local Layer 1 wrapper planning: `/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/research.md`
- Local Layer 2 comments insert planning: `/Users/ctgunn/Projects/youtube-mcp-server/specs/217-comments-insert/research.md`
- Official YouTube Data API `comments.update`: https://developers.google.com/youtube/v3/docs/comments/update
- Official YouTube Data API `comments` resource: https://developers.google.com/youtube/v3/docs/comments
- Official YouTube Data API quota cost table: https://developers.google.com/youtube/v3/determine_quota_cost
