# Research: Layer 2 Tool `comments_setModerationStatus`

## Decision: Expose `comments_setModerationStatus` as a low-level moderation status tool

**Rationale**: The seed slice YT-219 requires a Layer 2 tool named `comments_setModerationStatus` that maps directly to YouTube `comments.setModerationStatus`. The official comments reference describes this method as setting the moderation status of one or more comments, while separate methods own listing, insertion, updating, and deletion behavior.

**Alternatives considered**:

- Build a higher-level moderation workflow with recommendations or automatic decisions: rejected because Layer 2 tools must remain near-direct endpoint-backed operations.
- Combine comment editing and moderation behavior in one tool: rejected because `comments.update` and `comments.setModerationStatus` are separate upstream methods and separate seed slices.
- Add comment listing or preflight lookup into this tool: rejected because that would introduce cross-endpoint behavior outside the low-level Layer 2 contract.

## Decision: Require OAuth and expose quota cost 50 everywhere

**Rationale**: Official YouTube API guidance says the request must be authorized by the owner of the channel or video associated with the comments and requires the `youtube.force-ssl` scope. The official quota statement lists `comments.setModerationStatus` at 50 units. The Layer 1 YT-119 wrapper marks the endpoint as `oauth_required` and quota cost 50. The public contract must show this in metadata, description, usage notes, and examples before invocation.

**Alternatives considered**:

- Allow API-key-only access: rejected because comment moderation is a write operation requiring eligible OAuth authorization.
- Hide quota in implementation-only metadata: rejected by YT-202 and the constitution's contract-first requirement.
- Treat locally invalid requests as quota-bearing in examples: rejected because local validation should prevent unsupported requests from being sent upstream, while still documenting the official cost of actual endpoint calls.

## Decision: Use query-only inputs: `id`, `moderationStatus`, optional `banAuthor`, optional delegated owner context

**Rationale**: Official documentation defines all supported inputs as query parameters, requires `id` and `moderationStatus`, says `id` is a comma-separated list of comment IDs, accepts only `heldForReview`, `published`, and `rejected`, and forbids a request body. It also documents `banAuthor` as optional and valid only when `moderationStatus` is `rejected`. The local YT-119 Layer 1 wrapper preserves these same rules and also supports optional `onBehalfOfContentOwner` delegation.

**Alternatives considered**:

- Accept a request body for symmetry with insert/update tools: rejected because the upstream method explicitly has no request body.
- Accept one ID only: rejected because the upstream endpoint and existing Layer 1 validator support one or more IDs.
- Permit opaque pass-through parameters for forward compatibility: rejected because this project validates endpoint-specific request shapes before execution.

## Decision: Return a safe moderation acknowledgment for successful 204/no-content responses

**Rationale**: Official documentation says a successful `comments.setModerationStatus` call returns HTTP 204 No Content. Existing Layer 2 mutation tools include light wrapper context such as endpoint, quota cost, mutation status, auth context, and selected request context. For this endpoint, a safe acknowledgment should preserve target IDs, requested status, optional flag context, quota, endpoint identity, and safe OAuth/delegation context without fabricating comment resources.

**Alternatives considered**:

- Return a comment resource: rejected because the endpoint returns no content.
- Enrich with parent thread/channel/video metadata: rejected because this would cross endpoint boundaries and violate Layer 2 scope.
- Present moderation as a collection result: rejected because the endpoint is a mutation request with no returned list.

## Decision: Reuse the existing comments family module and tests

**Rationale**: YT-216 through YT-218 introduced and extended `src/mcp_server/tools/youtube_common/comments.py` and matching comments contract/unit/integration tests. Extending that module keeps related `comments_*` tools together and follows the resource-family pattern used by captions, channels, and channel sections.

**Alternatives considered**:

- Create a separate `comments_set_moderation_status.py`: rejected because it would split one resource family across files prematurely and duplicate registration/export patterns.
- Put the tool in generic shared contracts: rejected because endpoint-specific validation, examples, moderation-state caveats, optional-flag caveats, and acknowledgment result mapping belong to the concrete comments family.

## Decision: Map validation and upstream failures to shared safe Layer 2 categories

**Rationale**: YT-201/YT-202 shared contracts and existing comments tools use safe public categories such as `invalid_request`, `authentication_failed`, `authorization_failed`, `quota_exhausted`, `resource_not_found`, `endpoint_unavailable`, `deprecated_endpoint`, and `upstream_failure`. Official moderation errors include `banWithoutReject`, `operationNotSupported`, `processingFailure`, `forbidden`, and `commentNotFound`; these map naturally to shared categories without exposing raw upstream diagnostics.

**Alternatives considered**:

- Preserve raw upstream error detail names only: rejected because public MCP clients need stable shared categories and safe diagnostics.
- Collapse every moderation failure into `upstream_failure`: rejected because callers need to distinguish validation, authorization, quota, and missing target-comment outcomes.
- Add a new custom error taxonomy for comments moderation: rejected because YT-201 requires shared conventions across Layer 2 tools.

## Decision: Follow Red-Green-Refactor with focused contract, unit, integration, full-suite, and lint evidence

**Rationale**: The constitution makes Red-Green-Refactor non-negotiable and requires full repository test-suite execution after final code changes. The implementation should begin with failing tests for discovery, schema, validation, handler behavior, acknowledgment mapping, error mapping, examples, exports, and default registry integration.

**Alternatives considered**:

- Implementing first and adding tests afterward: rejected by the constitution.
- Running only focused tests: rejected because full-suite validation is required before completion.
- Omitting docstring work from planning: rejected because every new or changed Python function must have a reStructuredText docstring.

## Decision: No unresolved clarifications remain

**Rationale**: The seed, feature spec, constitution, current codebase, existing YT-119 wrapper, existing comments Layer 2 tools, and official documentation resolve the endpoint identity, quota, auth mode, required fields, accepted statuses, optional flag rules, response shape, dependencies, and validation boundaries.

**Alternatives considered**:

- Ask for additional scope confirmation: rejected because the feature description explicitly names YT-219 and the seed provides enough scope detail.

## Sources

- Local seed: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`
- Local feature spec: `/Users/ctgunn/Projects/youtube-mcp-server/specs/219-comments-set-moderation-status/spec.md`
- Local Layer 1 wrapper planning: `/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/spec.md`
- Local Layer 2 comments update planning: `/Users/ctgunn/Projects/youtube-mcp-server/specs/218-comments-update/research.md`
- Official YouTube Data API `comments.setModerationStatus`: https://developers.google.com/youtube/v3/docs/comments/setModerationStatus
- Official YouTube Data API quota cost table: https://developers.google.com/youtube/v3/determine_quota_cost
