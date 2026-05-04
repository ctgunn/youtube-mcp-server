# Research: YT-141 Layer 1 Endpoint `subscriptions.list`

## Decision: Model `subscriptions.list` auth as mixed or conditional based on selector mode

**Rationale**: The local tool inventory already describes `subscriptions.list` as `api_key` or mixed depending on filter mode, and neighboring Layer 1 list wrappers use selector-driven auth review surfaces rather than one global auth assumption. Keeping YT-141 mixed or conditional makes public-compatible paths and OAuth-backed subscriber-management paths reviewable before implementation details are inspected. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/110-channels-list-wrapper/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`

**Alternatives considered**:

- Model all selectors as `api_key` paths. Rejected because `mine`, `myRecentSubscribers`, and `mySubscribers` are self-scoped or subscriber-management paths that should remain distinct from public access.
- Model all selectors as `oauth_required`. Rejected because `channelId` and `id` remain viable public-compatible lookup paths in local planning artifacts.
- Hide selector-auth differences in runtime behavior only. Rejected because maintainers need contract-visible OAuth rules before implementation inspection.

## Decision: Use exactly-one-selector validation across `channelId`, `id`, `mine`, `myRecentSubscribers`, and `mySubscribers`

**Rationale**: The shared `EndpointRequestShape` contract already supports mutually exclusive selector validation, and nearby list wrappers consistently treat selector choice as deterministic and exclusive. Reusing that pattern keeps `subscriptions.list` requests predictable and reviewable for both public and owner-scoped retrieval paths. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/contracts/layer1-playlists-list-filter-modes-contract.md`

**Alternatives considered**:

- Allow multiple selectors and let upstream precedence decide. Rejected because caller behavior becomes ambiguous and harder to test.
- Silently rewrite conflicting selectors to one preferred mode. Rejected because hidden coercion weakens Layer 1 reviewability.
- Limit YT-141 to only one or two selectors. Rejected because the feature spec explicitly names the broader selector set for this slice.

## Decision: Treat `channelId` and `id` as public-compatible selectors and `mine`, `myRecentSubscribers`, and `mySubscribers` as OAuth-backed selectors

**Rationale**: This mapping is the smallest consistent interpretation of the local spec and tool inventory: public channel-oriented lookup paths remain usable without owner context, while self-scoped and subscriber-management retrieval requires stronger authorization. The decision also aligns with the repository’s existing pattern where owner-scoped selectors such as `mine` are reviewable as OAuth-backed paths. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/110-channels-list-wrapper/contracts/layer1-channels-list-auth-filter-contract.md`

**Alternatives considered**:

- Treat `id` as OAuth-backed because subscriptions can reference private relationships. Rejected because the local planning artifacts do not require that extra restriction for direct lookup paths.
- Treat `myRecentSubscribers` and `mySubscribers` as public-compatible paths. Rejected because they describe subscriber-management style retrieval rather than public channel discovery.
- Collapse all OAuth-backed selectors into a single undocumented “private mode.” Rejected because the spec requires filter modes and OAuth requirements to stay explicit.

## Decision: Require `part` plus exactly one selector as the minimum supported request shape

**Rationale**: Nearby Layer 1 list wrappers keep `part` explicit in metadata and validation, and the local Layer 2 inventory for `subscriptions.list` includes `part` alongside the selector set. Requiring `part` plus one selector gives YT-141 a stable, reviewable boundary that remains close to the near-raw endpoint surface. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/spec.md`

**Alternatives considered**:

- Allow selector-only requests and infer `part`. Rejected because current Layer 1 patterns keep `part` visible instead of silently defaulting it.
- Permit loosely shaped payloads and defer field rules to transport. Rejected because the shared request-shape contract exists to make boundaries reviewable before execution.
- Require additional fields such as `order` for all requests. Rejected because ordering is optional and selector-dependent in this slice.

## Decision: Preserve upstream-style paging through `pageToken` and `maxResults` for collection-style selector modes, while treating direct `id` lookup as non-paged

**Rationale**: The local tool inventory names `pageToken` and `maxResults` for `subscriptions.list`, and neighboring list-wrapper plans keep collection-style retrieval close to upstream pagination concepts rather than remapping them. The smallest deterministic rule is to support paging for selector modes that can span a collection and treat `id` lookup as direct retrieval without paging expectations. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/contracts/layer1-playlists-list-filter-modes-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/spec.md`

**Alternatives considered**:

- Support paging for every selector including `id`. Rejected because direct identifier lookup should remain deterministic and reviewable without continuation semantics.
- Omit paging from the wrapper contract and leave it for later layers. Rejected because the feature spec explicitly calls out pagination behavior.
- Remap paging to internal names such as `pageSize`. Rejected because Layer 1 stays close to upstream request parameters.

## Decision: Keep `order` reviewable as an optional near-raw field only for selector modes that remain collection-style in this slice

**Rationale**: The local tool inventory includes `order` for `subscriptions.list`, but the feature spec asks for selector-mode constraints to stay visible. The smallest planning-safe decision is to preserve `order` as an optional near-raw field for collection-style selectors and document that direct `id` lookup does not rely on ordering. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/quickstart.md`

**Alternatives considered**:

- Remove `order` from the wrapper contract entirely. Rejected because the local inventory already includes it for this endpoint.
- Promise every upstream ordering variant unconditionally. Rejected because the repository’s planning style prefers selector-aware boundaries over speculative broad support.
- Treat `order` as required for subscriber-management selectors. Rejected because the spec positions ordering as optional behavior, not a mandatory request element.

## Decision: Preserve explicit boundaries between invalid request shapes, under-authorized selector paths, empty-result success, and normalized upstream subscription failures

**Rationale**: YT-141 requires downstream callers to distinguish malformed requests, incompatible selector or paging combinations, requests that need stronger authorization, valid empty subscription results, and genuine upstream failures. Nearby list-wrapper artifacts treat these outcome classes as separate and reviewable, which keeps later layers predictable. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/110-channels-list-wrapper/research.md`

**Alternatives considered**:

- Flatten empty results and failures into one generic unsuccessful outcome. Rejected because downstream remediation differs substantially.
- Treat all OAuth-dependent selector paths as unsupported instead of access-constrained. Rejected because the repository already models mixed or conditional auth explicitly.
- Expand to a much larger failure taxonomy now. Rejected because the spec only requires separation of the major outcome types.

## Decision: Keep the implementation seam centered on `wrappers.py`, `youtube.py`, `consumer.py`, `__init__.py`, and the existing Layer 1 metadata, integration, and transport tests

**Rationale**: Nearby list wrappers already extend these files rather than creating a new integration submodule for each endpoint. The existing unit, contract, integration, and transport suites provide the smallest Red-Green-Refactor seam for metadata review, request-shape validation, request construction, and higher-layer summary behavior. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

**Alternatives considered**:

- Create a new subscriptions-specific integration module for one endpoint slice. Rejected because one wrapper does not justify new architecture.
- Limit validation to metadata-only checks. Rejected because the constitution requires integration and regression coverage.
- Skip consumer-summary updates. Rejected because the spec expects maintainer-visible reuse guidance beyond raw transport details.

## Decision: Use two feature-local contracts mirroring the existing wrapper-plus-filter-modes pattern

**Rationale**: Nearby endpoint slices separate wrapper-level metadata requirements from more specific selector, auth, and filter behavior guidance. Reusing that split for YT-141 keeps one contract focused on wrapper identity, quota visibility, and request shape, and a second focused on selector modes, OAuth behavior, paging and ordering boundaries, and failure interpretation. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/contracts/layer1-playlists-list-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/contracts/layer1-playlists-list-filter-modes-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/spec.md`

**Alternatives considered**:

- Use one contract file only. Rejected because wrapper requirements and selector behavior become harder to review cleanly together.
- Put all guidance in the plan and skip feature-local contracts. Rejected because the constitution requires contract-first design artifacts.
- Create a larger multi-endpoint subscriptions contract now. Rejected because this slice should stay scoped to one endpoint.

## Clarification Closure

All planning-time clarifications for YT-141 are resolved in this research artifact. No `NEEDS CLARIFICATION` markers remain.
