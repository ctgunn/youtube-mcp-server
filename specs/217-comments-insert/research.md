# Research: Layer 2 Tool `comments_insert`

## Decision: Expose `comments_insert` as a low-level reply creation tool

**Rationale**: The seed slice YT-217 requires a Layer 2 tool named `comments_insert` that maps directly to YouTube `comments.insert`. Official YouTube documentation describes `comments.insert` as creating a reply to an existing comment and explicitly routes top-level comment creation to `commentThreads.insert`.

**Alternatives considered**:

- Include top-level comment-thread creation in the same tool: rejected because official endpoint ownership and the feature spec keep that behavior out of scope.
- Build a higher-level conversation workflow: rejected because Layer 2 tools must remain near-direct endpoint-backed operations.

## Decision: Require OAuth and expose quota cost 50 everywhere

**Rationale**: Official documentation states that `comments.insert` requires authorization and has quota cost 50. The Layer 1 YT-117 wrapper also marks the endpoint as `oauth_required` and quota cost 50. The public contract must show this in metadata, description, usage notes, and examples before invocation.

**Alternatives considered**:

- Allow API-key-only access: rejected because comment insertion is a write operation requiring eligible OAuth authorization.
- Hide quota in implementation-only metadata: rejected by YT-202 and the constitution's contract-first requirement.

## Decision: Require `part`, `body.snippet.parentId`, and `body.snippet.textOriginal`

**Rationale**: Official documentation requires `part`, accepts `id` and `snippet` response parts, and requires the request body to include `snippet.parentId` and `snippet.textOriginal`. The local Layer 1 wrapper validates `part`, `body`, parent ID, and reply text through the existing `comments.insert` wrapper contract.

**Alternatives considered**:

- Permit metadata-only requests: rejected because the endpoint requires a comment resource body.
- Permit parent ID outside the body: rejected because the upstream resource model places it in `body.snippet.parentId`.
- Permit empty text for placeholder replies: rejected because official errors include `commentTextRequired`.

## Decision: Return a near-raw created comment resource result

**Rationale**: Official documentation returns a comment resource in the response body when insertion succeeds. Existing Layer 2 mutation tools return light wrapper context such as endpoint, quota cost, requested parts, mutation status, and item while preserving upstream fields.

**Alternatives considered**:

- Return only an acknowledgment: rejected because the endpoint returns a comment resource and callers need the created comment identity.
- Enrich with parent thread/channel/video metadata: rejected because this would cross endpoint boundaries and violate Layer 2 scope.

## Decision: Reuse the existing comments family module and tests

**Rationale**: YT-216 already introduced `src/mcp_server/tools/youtube_common/comments.py` and matching comments contract/unit/integration tests. Extending that module keeps related `comments_*` tools together and follows the existing resource-family pattern used by captions, channels, and channel sections.

**Alternatives considered**:

- Create a separate `comments_insert.py`: rejected because it would split one resource family across files prematurely and duplicate registration/export patterns.
- Put the tool in generic shared contracts: rejected because endpoint-specific validation, examples, and caveats belong to the concrete comments family.

## Decision: Map validation and upstream failures to shared safe Layer 2 categories

**Rationale**: YT-201/YT-202 shared contracts and existing `comments_list` behavior use safe public categories such as `invalid_request`, `authentication_failed`, `authorization_failed`, `quota_exhausted`, `resource_not_found`, `endpoint_unavailable`, and `upstream_failure`. Official insert errors map naturally to those categories without exposing raw upstream diagnostics.

**Alternatives considered**:

- Preserve raw upstream error detail names only: rejected because public MCP clients need stable shared categories and safe diagnostics.
- Collapse every publish failure into `upstream_failure`: rejected because callers need to distinguish validation, authorization, quota, and missing parent-comment outcomes.

## Decision: No unresolved clarifications remain

**Rationale**: The seed, feature spec, constitution, current codebase, and official documentation resolve the endpoint identity, quota, auth mode, required fields, response shape, dependencies, and validation boundaries.

**Alternatives considered**:

- Ask for additional scope confirmation: rejected because the feature description explicitly names YT-217 and the seed provides enough scope detail.

## Sources

- Local seed: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`
- Local feature spec: `/Users/ctgunn/Projects/youtube-mcp-server/specs/217-comments-insert/spec.md`
- Local Layer 1 wrapper: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/comments.py`
- Official YouTube Data API `comments.insert`: https://developers.google.com/youtube/v3/docs/comments/insert
- Official YouTube Data API `comments` resource: https://developers.google.com/youtube/v3/docs/comments
