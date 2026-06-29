# Research: Layer 2 Tool `commentThreads_insert`

## Decision: Expose `commentThreads_insert` as a low-level top-level comment-thread creation tool

**Rationale**: The seed slice YT-222 requires a Layer 2 tool named `commentThreads_insert` that maps directly to YouTube `commentThreads.insert`. The official YouTube reference describes this method as creating a new top-level comment and directs reply creation to `comments.insert`. This matches the Layer 2 requirement to expose endpoint-backed operations without higher-level composition.

**Alternatives considered**:

- Include reply creation in the same tool: rejected because official endpoint ownership and the feature spec keep reply creation out of scope.
- Build a higher-level conversation workflow: rejected because Layer 2 tools must remain near-direct endpoint-backed operations.
- Add moderation or generated-comment helpers: rejected because those are separate endpoint or Layer 3 concerns.

## Decision: Require OAuth and expose quota cost 50 everywhere

**Rationale**: The official YouTube reference states that `commentThreads.insert` requires authorization and has a quota cost of 50 units. The local Layer 1 YT-122 wrapper also marks the endpoint as `oauth_required` with quota cost 50. The public contract must show this in metadata, description, usage notes, and examples before invocation.

**Alternatives considered**:

- Allow API-key-only access: rejected because comment-thread insertion is a write operation requiring eligible OAuth authorization.
- Hide quota in implementation-only metadata: rejected by YT-202 and the constitution's contract-first requirement.
- Treat missing OAuth as an ordinary validation error: rejected because callers need to distinguish missing credentials from malformed request content.

## Decision: Require `part`, `body.snippet.channelId`, `body.snippet.videoId`, and `body.snippet.topLevelComment.snippet.textOriginal`

**Rationale**: The official YouTube reference requires a `part` query parameter and says the request body must provide a `commentThread` resource with `snippet.channelId`, `snippet.videoId`, and `snippet.topLevelComment.snippet.textOriginal`. The local Layer 1 wrapper validates a video-targeted top-level comment-thread body and accepts optional delegated owner context.

**Alternatives considered**:

- Permit metadata-only requests: rejected because the endpoint requires a comment-thread resource body.
- Permit video ID outside the body: rejected because the upstream resource model places target context inside `body.snippet`.
- Make channel ID optional in the Layer 2 contract: rejected because the current official reference lists it as a required property alongside `snippet.videoId`.
- Permit empty top-level text for placeholders: rejected because official errors include `commentTextRequired`.

## Decision: Return a near-raw created comment-thread resource result

**Rationale**: The official YouTube reference returns a `commentThread` resource when insertion succeeds. Existing Layer 2 mutation tools return light wrapper context such as endpoint, quota cost, requested parts, mutation status, safe auth context, delegation context, and returned item while preserving upstream fields.

**Alternatives considered**:

- Return only an acknowledgment: rejected because the endpoint returns a comment-thread resource and callers need the created thread identity.
- Enrich with channel, video, replies, moderation, or analytics data: rejected because this would cross endpoint boundaries and violate Layer 2 scope.
- Return a list-shaped payload: rejected because insertion creates a single resource.

## Decision: Reuse the existing comment threads family module and tests

**Rationale**: YT-221 introduced `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py` and matching comment-thread contract/unit/integration tests. Extending that module keeps related `commentThreads_*` tools together and follows the resource-family pattern used by captions, channels, channel sections, and comments.

**Alternatives considered**:

- Create a separate `comment_threads_insert.py`: rejected because it would split one resource family across files prematurely and duplicate registration/export patterns.
- Put the tool in `comments.py`: rejected because `comments_*` tools map to the `comments` resource while this feature maps to `commentThreads`.
- Put endpoint-specific validation in generic shared contracts: rejected because top-level comment-thread body rules, examples, and caveats belong to the concrete resource family.

## Decision: Map validation and upstream failures to shared safe Layer 2 categories

**Rationale**: YT-201/YT-202 shared contracts and existing Layer 2 tools use safe public categories such as `invalid_request`, `authentication_failed`, `authorization_failed`, `quota_exhausted`, `resource_not_found`, `endpoint_unavailable`, `deprecated_endpoint`, and `upstream_failure`. Official insert errors map naturally to those categories without exposing raw upstream diagnostics.

**Alternatives considered**:

- Preserve raw upstream error payloads only: rejected because public MCP clients need stable shared categories and safe diagnostics.
- Collapse every publish failure into `upstream_failure`: rejected because callers need to distinguish validation, authorization, quota, disabled-comment, missing channel, and missing video outcomes.
- Add a custom taxonomy for `commentThreads_insert`: rejected because Layer 2 tools must share error conventions.

## Decision: Follow Red-Green-Refactor with focused contract, unit, integration, full-suite, and lint evidence

**Rationale**: The constitution makes Red-Green-Refactor non-negotiable and requires full repository test-suite execution after final code changes. The implementation should begin with failing tests for discovery, schema, validation, handler behavior, result mapping, error mapping, examples, exports, and default registry integration.

**Alternatives considered**:

- Implement first and add tests afterward: rejected by the constitution.
- Run only focused tests: rejected because full-suite validation is required before completion.
- Omit docstring work from planning: rejected because every new or changed Python function must have a reStructuredText docstring.

## Decision: No unresolved clarifications remain

**Rationale**: The seed, feature spec, constitution, current codebase, existing YT-122 wrapper, neighboring Layer 2 tools, and official documentation resolve the endpoint identity, quota, auth mode, required fields, response shape, dependencies, and validation boundaries.

**Alternatives considered**:

- Ask for additional scope confirmation: rejected because the feature description explicitly names YT-222 and the seed provides enough scope detail.

## Sources

- Local seed: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`
- Local feature spec: `/Users/ctgunn/Projects/youtube-mcp-server/specs/222-comment-threads-insert/spec.md`
- Local Layer 1 wrapper: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/comment_threads.py`
- Local neighboring Layer 2 plan: `/Users/ctgunn/Projects/youtube-mcp-server/specs/221-comment-threads-list/plan.md`
- Local sibling mutation plan: `/Users/ctgunn/Projects/youtube-mcp-server/specs/217-comments-insert/plan.md`
- Official YouTube Data API `commentThreads.insert`: https://developers.google.com/youtube/v3/docs/commentThreads/insert
