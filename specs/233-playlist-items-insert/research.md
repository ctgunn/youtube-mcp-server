# Research: Layer 2 Tool `playlistItems_insert`

## Decision: Extend the Existing Playlist Items Layer 2 Module

**Decision**: Implement `playlistItems_insert` by extending `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py`.

**Rationale**: YT-232 already established the Layer 2 playlist-items resource-family module for `playlistItems_list`, and the existing family layout keeps endpoint-backed tools grouped by YouTube resource. Extending this module preserves cohesion, keeps public exports predictable through `youtube_common.__init__`, and avoids adding another package or mixing playlist item behavior into playlist image or playlist modules.

**Alternatives considered**:

- Create a new `playlist_items_insert.py` file: rejected because it fragments a single resource family and diverges from existing family modules such as comments, comment threads, channel sections, and playlist images.
- Add insert behavior to a generic shared mutation module: rejected because endpoint-specific validation, examples, and result context are easier to review in the resource-family module.
- Implement through a higher-level playlist workflow: rejected because YT-233 is a low-level Layer 2 endpoint tool, not a Layer 3 curation workflow.

## Decision: Reuse the YT-133 Layer 1 Wrapper

**Decision**: Use `build_playlist_items_insert_wrapper()` from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/playlist_items.py` as the endpoint execution dependency.

**Rationale**: The Layer 1 wrapper already records `playlistItems.insert`, HTTP `POST`, quota cost `50`, OAuth-required auth mode, and required `part` plus `body` request shape. Reusing it honors the Layer 2 rule that public endpoint tools expose existing Layer 1 behavior rather than redefining upstream execution.

**Alternatives considered**:

- Duplicate upstream execution in Layer 2: rejected because it would bypass shared auth, quota, request, and error conventions.
- Change the Layer 1 wrapper preemptively: rejected unless tests reveal a concrete metadata, validation, or export gap.
- Mock insertion behavior only: rejected because the public tool must be endpoint-backed, with test doubles limited to verification.

## Decision: Require OAuth-Backed Access

**Decision**: `playlistItems_insert` must advertise and enforce OAuth-backed access; API-key-only access is not supported for this mutation.

**Rationale**: Playlist item insertion modifies a playlist and the existing Layer 1 wrapper uses `OAUTH_REQUIRED`. The public contract must make this visible before invocation through metadata, descriptions, usage notes, examples, and safe access errors.

**Alternatives considered**:

- Allow API-key execution: rejected because it conflicts with the mutation access requirement.
- Leave access implicit: rejected because the spec and YT-202 require visible auth mode disclosure.
- Treat missing OAuth as a generic validation error: rejected because callers need to distinguish authorization failures from malformed request bodies.

## Decision: Preserve the Upstream Mutation Shape with Focused Validation

**Decision**: The input contract requires `part` and a `body` object containing writable playlist/video assignment data, centered on `body.snippet.playlistId` and `body.snippet.resourceId.videoId`. Placement inputs are supported only when explicitly documented; unsupported optional fields and read-only fields must be rejected.

**Rationale**: This keeps the tool close to `playlistItems.insert` while protecting callers from ambiguous mutations. It also mirrors YT-133's Layer 1 contract, which requires a writable `body.snippet` payload carrying playlist and referenced video details.

**Alternatives considered**:

- Flatten playlist and video identifiers into top-level fields: rejected because Layer 2 tools should stay close to upstream semantics.
- Accept arbitrary request bodies and rely on upstream errors: rejected because local validation must provide clear caller-facing feedback for unsupported shapes.
- Add playlist generation, search, or enrichment helpers: rejected because those are higher-level workflows outside YT-233.

## Decision: Use Near-Raw Created Resource Results with Safe Context

**Decision**: Successful results should preserve the created playlist-item resource and add safe context including endpoint identity, quota cost, selected parts, assignment context, placement context when applicable, and authorization mode.

**Rationale**: Existing Layer 2 mutation tools return near-raw resources with enough context for MCP callers to understand the mutation outcome without fabricated enrichment. This satisfies the spec's requirement to preserve returned upstream fields and keep playlist, video, channel, transcript, ranking, analytics, and recommendation data out of scope.

**Alternatives considered**:

- Return only the upstream object: rejected because callers need consistent quota, endpoint, and request context.
- Return a high-level curation summary: rejected because that would masquerade as a Layer 3 workflow.
- Store created playlist items for later lookup: rejected because this slice has no persistence requirement.

## Decision: Follow Shared Safe Error Categories

**Decision**: Map validation, authentication, authorization, quota, duplicate or ineligible resource, missing resource, endpoint unavailable, deprecated behavior, and unexpected upstream failures into safe Layer 2 categories without exposing credentials, raw upstream bodies, stack traces, or unsafe request context.

**Rationale**: The constitution requires secure, deterministic tooling, and existing Layer 2 tools sanitize details before exposing errors. Insert failures can be caused by local body mistakes, missing OAuth access, playlist ownership, duplicate or ineligible videos, quota, or upstream availability; callers need these categories to be distinguishable.

**Alternatives considered**:

- Pass through raw upstream errors: rejected because raw diagnostics can expose sensitive details and are less stable for MCP clients.
- Collapse all failures into invalid request: rejected because it hides access, quota, missing resource, and upstream availability distinctions.
- Add endpoint-specific bespoke categories everywhere: rejected because shared Layer 2 categories are already sufficient for this slice.

## Decision: Verification Uses Focused Tests, Full Suite, and Ruff

**Decision**: Planning and tasks must require focused contract/unit/integration tests for `playlistItems_insert`, then final `pytest` and `ruff check .`.

**Rationale**: The constitution mandates Red-Green-Refactor, integration and regression coverage, full repository test-suite execution, code-quality checks, and reStructuredText docstrings for new or changed Python functions. The focused tests make the endpoint contract reviewable before the full suite confirms there is no broader regression.

**Alternatives considered**:

- Focused tests only: rejected because the constitution requires a full-suite run.
- Full suite only: rejected because endpoint-specific contract failures should be explicit and fast to diagnose.
- Skip lint for planning: rejected because existing neighboring plans include Ruff as the code-quality check.
