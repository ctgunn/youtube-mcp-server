# Research: YT-136 Layer 1 Endpoint `playlists.list`

## Decision: Support exactly one selector path per request using `channelId`, `id`, or `mine`

**Rationale**: The local tool inventory for `playlists.list` names `channelId`, `id`, and `mine` as the core filter modes, and adjacent conditional-auth list wrappers already treat selector sets as mutually exclusive rather than permissive combinations. The smallest stable wrapper contract is therefore one required `part` field plus exactly one active selector from `channelId`, `id`, or `mine`, with no silent precedence between modes. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`

**Alternatives considered**:

- Support only `channelId` and `id` in this slice. Rejected because the current specification requires the wrapper contract to document whether `mine` is supported, and the codebase already uses conditional-auth selector patterns for owner-scoped list retrieval.
- Allow multiple primary selectors in one request. Rejected because current Layer 1 wrappers use deterministic selector contracts and reject conflicting selector combinations before execution.
- Treat selector choice as implicit from whatever fields happen to be present. Rejected because silent selector precedence would make higher-layer reuse and failure analysis harder.

## Decision: Model `playlists.list` as a conditional-auth wrapper

**Rationale**: Existing Layer 1 list wrappers already encode mixed public and owner-scoped behavior with `AuthMode.CONDITIONAL`, plus an auth-condition note that explains which selector requires which auth path. `playlists.list` fits that pattern cleanly: `channelId` and `id` stay on the public API-key path, while `mine` remains the owner-scoped OAuth-backed path. This preserves the behavior implied by the local tool catalog while keeping the contract specific enough for review. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/auth.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Alternatives considered**:

- Model the wrapper as API-key-only. Rejected because that would exclude the owner-scoped `mine` path named in the tool catalog and specification.
- Model the wrapper as OAuth-required for all requests. Rejected because that would over-constrain public playlist lookup modes and conflict with existing conditional-auth list-wrapper precedent.
- Leave auth behavior unspecified in metadata and decide only at runtime. Rejected because maintainers need the access boundary visible before reading implementation details.

## Decision: Require `part` and keep request validation deterministic through the existing `EndpointRequestShape` contract

**Rationale**: Existing Layer 1 list wrappers require `part`, reject undocumented top-level fields, and then use exactly-one-selector plus endpoint-specific validators for selector-sensitive rules. The smallest path for YT-136 is to follow that sequence rather than inventing a new validation style. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`

**Alternatives considered**:

- Validate `part` against an endpoint-specific whitelist now. Rejected because current Layer 1 list wrappers do not do that, and the feature does not require broader shared contract changes.
- Accept undocumented top-level modifiers for flexibility. Rejected because current wrapper request shapes reject unsupported fields before executor dispatch.
- Push request-shape enforcement down into transport logic only. Rejected because the repository already centers deterministic validation in wrapper contracts.

## Decision: Allow paging for collection-style selectors `channelId` and `mine`, and reject paging for direct `id` lookup

**Rationale**: Adjacent list-wrapper planning already uses selector-aware paging enforcement: collection-oriented retrieval paths page, while direct ID lookup remains deterministic without paging. Applying that same pattern to `playlists.list` keeps paging reviewable and minimal while fitting both public and owner-scoped collection retrieval modes. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/128-playlist-images-list/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/132-playlist-items-list/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/spec.md`

**Alternatives considered**:

- Allow `pageToken` and `maxResults` for all selector modes because the inventory lists them generically. Rejected because direct `id` lookup does not need paging and the feature specification requires filter-specific paging guidance.
- Reject paging entirely in this slice. Rejected because the seed explicitly calls out pagination behavior for YT-136.
- Support paging only for `channelId` but not `mine`. Rejected because owner-scoped playlist retrieval is still a collection-style path and would be artificially constrained by a narrower rule.

## Decision: Make quota cost `1`, selector-aware auth expectations, filter rules, and empty-result behavior visible in metadata, docstrings, consumer summaries, and contract artifacts

**Rationale**: The YT-136 seed requires the official quota cost of `1` to be recorded in metadata and method comments or docstrings, and the specification requires filter modes plus paging behavior to be reviewable by maintainers. Existing Layer 1 slices keep quota and request behavior discoverable through wrapper metadata, feature-local contracts, higher-layer summary surfaces, and tests. YT-136 should follow that pattern while also making it explicit that valid playlist lookups may return zero items without being treated as wrapper failures. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`

**Alternatives considered**:

- Keep quota and auth visibility only in planning docs. Rejected because the seed requires metadata and docstring visibility.
- Treat empty results as an implicit error because no playlists matched. Rejected because nearby list-wrapper planning already preserves empty results as successful no-match outcomes.
- Put filter and paging guidance only in tests. Rejected because higher-layer authors need reviewable contracts before reading test code.

## Decision: Preserve explicit failure boundaries between invalid selector shapes, incompatible auth usage, and successful no-match retrievals

**Rationale**: The YT-136 specification requires downstream callers to distinguish invalid or unsupported request combinations from access-related failures. Existing Layer 1 conditional-auth list wrappers already separate selector-validation failures from auth mismatches, and the shared executor model preserves successful empty item lists as distinct from failures. The smallest useful split is therefore to keep invalid request shapes, auth mismatches, and successful no-match results reviewable as different outcomes. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Alternatives considered**:

- Flatten selector and auth failures into one generic invalid-request outcome. Rejected because caller remediation differs when the selector is malformed versus when the auth mode is incompatible.
- Treat access mismatches as silent selector fallbacks. Rejected because that would hide contract boundaries and make behavior nondeterministic.
- Over-specialize local failure categories beyond the feature need. Rejected because one clear split between validation, auth, and successful no-match outcomes is sufficient for higher-layer planning.

## Decision: Keep the implementation seam centered on `wrappers.py`, `youtube.py`, `consumer.py`, `__init__.py`, and the existing Layer 1 test suites

**Rationale**: `wrappers.py` already contains the endpoint-specific builder and selector-validation pattern used by neighboring list wrappers, `youtube.py` is the transport seam for request construction and normalized response parsing, `consumer.py` already exposes higher-layer summaries for internal list wrappers, `__init__.py` exports endpoint builders, and the existing unit, contract, integration, and transport tests already cover adjacent Layer 1 retrieval features with minimal duplication. This is the smallest extension path for one more playlist-family list endpoint slice. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

**Alternatives considered**:

- Create a new dedicated playlists module for one endpoint slice. Rejected because the repository already has an endpoint-wrapper home and one slice does not justify new architecture.
- Limit validation to metadata-only tests. Rejected because the constitution requires integration and regression coverage.
- Skip higher-layer summary updates. Rejected because nearby wrapper slices already use consumer summaries to prove downstream reviewability.

## Clarification Closure

All planning-time clarifications for YT-136 are resolved in this research artifact. No `NEEDS CLARIFICATION` markers remain.
