# Research: Layer 2 Tool `comments_delete`

## Decision: Expose `comments_delete` as a low-level destructive deletion tool

**Rationale**: The seed slice YT-220 requires a Layer 2 tool named `comments_delete` that maps directly to YouTube `comments.delete`. The official comments reference describes this method as deleting a comment, while separate methods own listing, insertion, updating, and moderation status changes.

**Alternatives considered**:

- Build a higher-level cleanup workflow with search, review, or recovery behavior: rejected because Layer 2 tools must remain near-direct endpoint-backed operations.
- Combine comment moderation and deletion behavior in one tool: rejected because `comments.setModerationStatus` and `comments.delete` are separate upstream methods and separate seed slices.
- Add comment lookup or confirmation into this tool: rejected because that would introduce cross-endpoint behavior outside the low-level Layer 2 contract.

## Decision: Require OAuth and expose quota cost 50 everywhere

**Rationale**: The official YouTube API reference says `comments.delete` requires authorization with the `youtube.force-ssl` scope and has quota cost 50. The Layer 1 YT-120 wrapper marks the endpoint as `oauth_required` and quota cost 50. The public contract must show this in metadata, description, usage notes, and examples before invocation.

**Alternatives considered**:

- Allow API-key-only access: rejected because comment deletion is a destructive write operation requiring eligible OAuth authorization.
- Hide quota in implementation-only metadata: rejected by YT-202 and the constitution's contract-first requirement.
- Treat locally invalid requests as quota-bearing in examples: rejected because local validation should prevent unsupported requests from being sent upstream, while still documenting the official cost of actual endpoint calls.

## Decision: Use query-only input: required `id` plus optional delegated owner context

**Rationale**: Official documentation defines `id` as the required query parameter that specifies the comment resource being deleted and says not to provide a request body. The local YT-120 Layer 1 wrapper preserves the required target-comment ID and also supports optional `onBehalfOfContentOwner` delegation.

**Alternatives considered**:

- Accept a request body for symmetry with insert/update tools: rejected because the upstream method explicitly has no request body.
- Accept one request containing multiple IDs: rejected because the official `comments.delete` method requires one `id` string for the resource being deleted and the Layer 1 wrapper is scoped to one comment deletion attempt.
- Permit opaque pass-through parameters for forward compatibility: rejected because this project validates endpoint-specific request shapes before execution.

## Decision: Return a safe deletion acknowledgment for successful 204/no-content responses

**Rationale**: Official documentation says a successful `comments.delete` call returns HTTP 204 No Content. Existing Layer 2 mutation tools include light wrapper context such as endpoint, quota cost, mutation status, auth context, and selected request context. For this endpoint, a safe acknowledgment should preserve target ID, quota, endpoint identity, and safe OAuth/delegation context without fabricating a deleted comment resource.

**Alternatives considered**:

- Return a deleted comment resource: rejected because the endpoint returns no content.
- Enrich with parent thread/channel/video metadata: rejected because this would cross endpoint boundaries and violate Layer 2 scope.
- Present deletion as a collection result: rejected because the endpoint is a single-resource destructive mutation with no returned list.

## Decision: Reuse the existing comments family module and tests

**Rationale**: YT-216 through YT-219 introduced and extended `src/mcp_server/tools/youtube_common/comments.py` and matching comments contract/unit/integration tests. Extending that module keeps related `comments_*` tools together and follows the resource-family pattern used by captions, channels, and channel sections.

**Alternatives considered**:

- Create a separate `comments_delete.py`: rejected because it would split one resource family across files prematurely and duplicate registration/export patterns.
- Put the tool in generic shared contracts: rejected because endpoint-specific validation, examples, destructive-operation caveats, and acknowledgment result mapping belong to the concrete comments family.

## Decision: Map validation and upstream failures to shared safe Layer 2 categories

**Rationale**: YT-201/YT-202 shared contracts and existing comments tools use safe public categories such as `invalid_request`, `authentication_failed`, `authorization_failed`, `quota_exhausted`, `resource_not_found`, `endpoint_unavailable`, `deprecated_endpoint`, and `upstream_failure`. Official deletion errors include `processingFailure`, `forbidden`, and `commentNotFound`; these map naturally to shared categories without exposing raw upstream diagnostics.

**Alternatives considered**:

- Preserve raw upstream error detail names only: rejected because public MCP clients need stable shared categories and safe diagnostics.
- Collapse every deletion failure into `upstream_failure`: rejected because callers need to distinguish validation, authorization, quota, and missing target-comment outcomes.
- Add a new custom error taxonomy for comments deletion: rejected because YT-201 requires shared conventions across Layer 2 tools.

## Decision: Follow Red-Green-Refactor with focused contract, unit, integration, full-suite, and lint evidence

**Rationale**: The constitution makes Red-Green-Refactor non-negotiable and requires full repository test-suite execution after final code changes. The implementation should begin with failing tests for discovery, schema, validation, handler behavior, acknowledgment mapping, error mapping, examples, exports, and default registry integration.

**Alternatives considered**:

- Implementing first and adding tests afterward: rejected by the constitution.
- Running only focused tests: rejected because full-suite validation is required before completion.
- Omitting docstring work from planning: rejected because every new or changed Python function must have a reStructuredText docstring.

## Decision: No unresolved clarifications remain

**Rationale**: The seed, feature spec, constitution, current codebase, existing YT-120 wrapper, existing comments Layer 2 tools, and official documentation resolve the endpoint identity, quota, auth mode, required field, response shape, dependencies, and validation boundaries.

**Alternatives considered**:

- Ask for additional scope confirmation: rejected because the feature description explicitly names YT-220 and the seed provides enough scope detail.

## Sources

- Local seed: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`
- Local feature spec: `/Users/ctgunn/Projects/youtube-mcp-server/specs/220-comments-delete/spec.md`
- Local Layer 1 wrapper planning: `/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/spec.md`
- Local Layer 2 comments moderation planning: `/Users/ctgunn/Projects/youtube-mcp-server/specs/219-comments-set-moderation-status/research.md`
- Official YouTube Data API `comments.delete`: https://developers.google.com/youtube/v3/docs/comments/delete
