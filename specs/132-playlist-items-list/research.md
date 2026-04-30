# Research: YT-132 Layer 1 Endpoint `playlistItems.list`

## Decision: Support exactly one selector path per request using `playlistId` or `id`

**Rationale**: The local feature seed for YT-132 commits to playlist and ID filter modes and requires their pagination behavior to be documented. Adjacent playlist-family precedent already uses deterministic selector contracts with explicit exclusivity rules rather than permissive multi-selector behavior. The smallest consistent request contract is therefore one required `part` field plus exactly one active selector from `playlistId` or `id`. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/132-playlist-items-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/128-playlist-images-list/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`

**Alternatives considered**:

- Support `playlistId`, `id`, and `videoId` in this slice. Rejected because the seed for YT-132 names playlist and ID modes, and adjacent playlist-family precedent does not justify broadening the contract further in this feature.
- Allow multiple primary selectors in one request. Rejected because current Layer 1 wrappers use deterministic selector sets and reject conflicting selector combinations before execution.
- Treat selector choice as implicit from whatever fields happen to be present. Rejected because silent selector precedence would make higher-layer reuse and failure analysis harder.

## Decision: Model the seed-required `playlistItems.list` selector set as API-key retrieval for this slice

**Rationale**: The local tool inventory records `playlistItems.list` as `api_key` or mixed depending on filter mode, which leaves room for broader future coverage. For this planning slice, however, the supported selector set is intentionally narrowed to `playlistId` and `id`. Keeping those paths on the public API-key side is the simplest contract that satisfies the feature while preserving room for later mixed-auth expansion in a separate slice if additional selector modes are introduced. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/132-playlist-items-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/auth.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/research.md`

**Alternatives considered**:

- Model the wrapper as mixed or conditional auth now. Rejected because the currently scoped selector set does not need owner-scoped behavior to satisfy the seed or specification.
- Require OAuth for all playlist-item retrieval. Rejected because that would over-constrain a read-only wrapper and conflict with the local inventory for the supported selector set.
- Leave auth behavior unspecified in metadata and decide only at runtime. Rejected because maintainers need the access boundary visible before reading implementation details.

## Decision: Require `part` and keep request validation deterministic through the existing `EndpointRequestShape` contract

**Rationale**: Existing Layer 1 list wrappers require `part`, reject undocumented top-level fields, and then use exactly-one-selector plus endpoint-specific validators for mode-sensitive rules. The smallest path for YT-132 is to follow that same sequence rather than inventing a new validation style. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`

**Alternatives considered**:

- Validate `part` against an endpoint-specific whitelist now. Rejected because current Layer 1 list wrappers do not do that, and the feature does not require broader shared contract changes.
- Accept undocumented top-level modifiers for flexibility. Rejected because current wrapper request shapes reject unsupported fields before executor dispatch.
- Push request-shape enforcement down into transport logic only. Rejected because the repository already centers deterministic validation in wrapper contracts.

## Decision: Allow paging only for `playlistId` requests and reject paging for `id`

**Rationale**: The local playlist-family precedent for list endpoints already uses selector-aware paging enforcement: collection-style selectors may page while direct ID lookup remains deterministic without paging. Applying that same pattern to `playlistItems.list` gives later layers a reviewable contract that is both predictable and minimal. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/128-playlist-images-list/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/132-playlist-items-list/spec.md`

**Alternatives considered**:

- Allow `pageToken` and `maxResults` for all selector modes because the inventory lists them generically. Rejected because the feature specification requires selector-specific paging guidance and clear rejection of unsupported paging combinations.
- Reject paging entirely in this slice. Rejected because the seed explicitly calls out pagination behavior for YT-132.
- Leave paging behavior unresolved until implementation. Rejected because Phase 0 must close planning-time contract questions.

## Decision: Make quota cost `1`, selector rules, API-key expectations, and empty-result behavior visible in metadata, docstrings, consumer summaries, and contract artifacts

**Rationale**: The YT-132 seed requires the official quota cost of `1` to be recorded in metadata and method comments or docstrings, and the specification requires selector modes plus paging behavior to be reviewable by maintainers. Existing Layer 1 slices keep quota and selector behavior discoverable through wrapper metadata, feature-local contracts, higher-layer summary surfaces, and tests. YT-132 should follow that pattern while also making it explicit that valid playlist-item lookups may return zero items without being treated as wrapper failures. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/132-playlist-items-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/128-playlist-images-list/contracts/layer1-playlist-images-list-wrapper-contract.md`

**Alternatives considered**:

- Keep quota visibility only in planning docs. Rejected because the seed requires metadata and docstring visibility.
- Treat empty results as an implicit error because no playlist items matched. Rejected because nearby list-wrapper planning already preserves empty results as successful no-match outcomes.
- Put selector and paging guidance only in tests. Rejected because higher-layer authors need reviewable contracts before reading test code.

## Decision: Preserve explicit failure boundaries between invalid selector shapes, incompatible auth usage, and successful no-match retrievals

**Rationale**: The YT-132 specification requires downstream callers to distinguish invalid or unsupported request combinations from access-related failures. Existing Layer 1 list wrappers already separate selector-validation failures from auth mismatches, and the shared executor model preserves successful empty item lists as distinct from failures. The smallest useful split is therefore to keep invalid request shapes, auth mismatches, and successful no-match results reviewable as different outcomes. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/132-playlist-items-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/research.md`

**Alternatives considered**:

- Flatten selector and auth failures into one generic invalid-request outcome. Rejected because caller remediation differs when the selector is malformed versus when the auth mode is incompatible.
- Treat access mismatches as silent selector fallbacks. Rejected because that would hide contract boundaries and make behavior nondeterministic.
- Over-specialize local failure categories beyond the feature need. Rejected because one clear split between validation, auth, and successful no-match outcomes is sufficient for higher-layer planning.

## Decision: Keep the implementation seam centered on `wrappers.py`, `youtube.py`, `consumer.py`, `__init__.py`, and the existing Layer 1 test suites

**Rationale**: `wrappers.py` already contains the endpoint-specific builder and selector-validation pattern used by neighboring list wrappers, `youtube.py` is the transport seam for request construction and normalized response parsing, `consumer.py` already exposes higher-layer summaries for internal list wrappers, `__init__.py` exports endpoint builders, and the existing unit, contract, integration, and transport tests already cover adjacent Layer 1 retrieval features with minimal duplication. This is the smallest extension path for one more playlist-family list endpoint slice. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

**Alternatives considered**:

- Create a new dedicated playlist-items module for one endpoint slice. Rejected because the repository already has an endpoint-wrapper home and one slice does not justify new architecture.
- Limit validation to metadata-only tests. Rejected because the constitution requires integration and regression coverage.
- Skip higher-layer summary updates. Rejected because nearby wrapper slices already use consumer summaries to prove downstream reviewability.

## Clarification Closure

All planning-time clarifications for YT-132 are resolved in this research artifact. No `NEEDS CLARIFICATION` markers remain.
