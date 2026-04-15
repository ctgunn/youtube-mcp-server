# Research: YT-116 Layer 1 Endpoint `comments.list`

## Decision: Support exactly one selector path per request using `id` for direct comment lookup or `parentId` for reply lookup

**Rationale**: The local feature spec defines YT-116 around the seed-required ID-based retrieval and parent-comment-based retrieval modes. Existing internal list-wrapper precedent uses deterministic selector contracts with explicit exclusivity rules rather than permissive multi-selector behavior. The smallest consistent request contract is therefore one required `part` field plus exactly one active selector from `id` or `parentId`, with optional pagination and text-format modifiers kept reviewable but bounded. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/116-comments-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`

**Alternatives considered**:

- Allow both `id` and `parentId` in one request. Rejected because current Layer 1 wrappers use deterministic selector sets and reject conflicting selector combinations before execution.
- Support every possible upstream selector in this slice. Rejected because the seed only requires the direct comment and parent-comment paths, and broadening the scope would dilute one endpoint-slice delivery.
- Treat selector choice as implicit from whatever fields happen to be present. Rejected because silent selector precedence would make higher-layer reuse and failure analysis harder.

## Decision: Model the seed-required `comments.list` paths as public API-key retrieval for this slice

**Rationale**: The local tool inventory records `comments.list` as `api_key or mixed, depending on filter mode`, which leaves room for broader future selector coverage. For this planning slice, however, the spec only commits to direct comment lookup by `id` and reply lookup by `parentId`. Those two supported paths can be modeled as standard public retrieval without introducing conditional auth complexity, which keeps YT-116 aligned with the simplest contract that satisfies the feature specification. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/116-comments-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/auth.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`

**Alternatives considered**:

- Model the wrapper as mixed or conditional auth now. Rejected because the currently scoped selector set does not need owner-scoped behavior to satisfy the seed or spec.
- Require OAuth for all comment retrieval. Rejected because that would over-constrain the supported retrieval modes and add unnecessary complexity to an internal read-only wrapper.
- Leave auth behavior unspecified in metadata and decide only at runtime. Rejected because maintainers need the access boundary visible before reading implementation details.

## Decision: Keep optional retrieval modifiers limited to pagination and text-format review surfaces

**Rationale**: The local tool inventory already identifies `pageToken`, `maxResults`, and `textFormat` as the main optional `comments.list` modifiers alongside the seed-required selectors. Keeping only those modifiers inside the supported wrapper contract preserves a near-raw retrieval feel for later layers without making the request shape open-ended. This matches the repository’s pattern of exposing a small, deterministic set of optional fields per wrapper slice. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/contracts/layer1-channel-sections-list-wrapper-contract.md`

**Alternatives considered**:

- Allow arbitrary extra query fields for maximum upstream flexibility. Rejected because current Layer 1 request shapes reject undocumented fields by design.
- Omit pagination and text-format modifiers entirely. Rejected because those modifiers are already part of the local tool inventory and help later layers reuse the wrapper without raw request assembly.
- Add write-oriented or moderation-related modifiers to prepare for future comment features. Rejected because that would mix separate endpoint concerns into one read-only retrieval slice.

## Decision: Make quota cost `1`, selector rules, and empty-result behavior visible in metadata, docstrings, and contract artifacts

**Rationale**: The YT-116 seed requires the official quota cost of `1` to be recorded in metadata and method comments or docstrings, and the specification requires supported lookup modes to be reviewable by maintainers. Existing Layer 1 slices keep quota and selector behavior discoverable through wrapper metadata, feature-local contracts, higher-layer summary surfaces, and tests. YT-116 should follow that pattern while also making it explicit that valid comment lookups may return zero items without being treated as wrapper failures. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/116-comments-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/research.md`

**Alternatives considered**:

- Keep quota visibility only in planning docs. Rejected because the seed requires metadata and docstring visibility.
- Treat empty results as an implicit error because no comments matched. Rejected because nearby list-wrapper planning already preserves empty results as successful no-match outcomes.
- Put selector guidance only in tests. Rejected because higher-layer authors need reviewable contracts before reading test code.

## Decision: Preserve explicit failure boundaries between invalid selector shapes, access mismatches, and successful no-match retrievals

**Rationale**: The YT-116 spec requires downstream callers to distinguish invalid or unsupported request combinations from access-related failures. Existing Layer 1 list wrappers already separate selector-validation failures from selector-auth mismatches, and the shared executor model preserves successful empty item lists as distinct from failures. The smallest useful split is therefore to keep invalid request shapes, auth mismatches, and successful no-match results reviewable as different outcomes. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/116-comments-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/contracts/layer1-channel-sections-list-auth-filter-contract.md`

**Alternatives considered**:

- Flatten selector and auth failures into one generic invalid-request outcome. Rejected because caller remediation differs when the selector is malformed versus when the auth mode is incompatible.
- Treat access mismatches as silent selector fallbacks. Rejected because that would hide contract boundaries and make behavior nondeterministic.
- Over-specialize local failure categories beyond the feature need. Rejected because one clear split between validation, auth, and successful no-match outcomes is sufficient for higher-layer planning.

## Decision: Keep the implementation seam centered on `wrappers.py`, `youtube.py`, `consumer.py`, and the existing Layer 1 test suites

**Rationale**: `wrappers.py` already contains the endpoint-specific builder and selector-validation pattern used by nearby list wrappers, `youtube.py` is the transport seam for request construction and normalized response parsing, `consumer.py` already exposes higher-layer summaries for internal list wrappers, and the existing unit, contract, integration, and transport tests already cover neighboring Layer 1 retrieval features with minimal duplication. This is the smallest extension path for one more list endpoint slice. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

**Alternatives considered**:

- Create a new dedicated comments module for one endpoint slice. Rejected because the repository already has an endpoint-wrapper home and one slice does not justify new architecture.
- Limit validation to metadata-only tests. Rejected because the constitution requires integration and regression coverage.
- Skip higher-layer summary updates. Rejected because nearby wrapper slices already use consumer summaries to prove downstream reviewability.

## Clarification Closure

All planning-time clarifications for YT-116 are resolved in this research artifact. No `NEEDS CLARIFICATION` markers remain.
