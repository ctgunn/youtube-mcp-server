# Research: YT-119 Layer 1 Endpoint `comments.setModerationStatus`

## Decision: Support one deterministic query-only moderation request shape using comment identifiers, one moderation status, and narrowly scoped moderation flags

**Rationale**: The local feature spec defines YT-119 around changing moderation status for one or more existing comments, not around broad comment mutation. The smallest request contract that satisfies the seed is therefore a query-only request using one required moderation status field plus one required identifier field that can carry one or more target comment IDs, with only the moderation flags that are directly tied to this endpoint's moderation behavior included in scope. Existing internal write-wrapper precedent uses deterministic request shapes with endpoint-specific validation rather than permissive pass-through behavior. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`

**Alternatives considered**:

- Support any upstream moderation request shape in this slice. Rejected because the seed only requires one endpoint wrapper and widening the contract would dilute one endpoint-slice delivery.
- Treat the moderation payload as opaque pass-through query parameters. Rejected because nearby Layer 1 write wrappers validate supported shapes before execution.
- Restrict the slice to a single comment ID per request. Rejected because the local tool inventory refers to comment identifiers in the plural and an internal moderation wrapper should preserve that reuse value.

## Decision: Model `comments.setModerationStatus` as an OAuth-required moderation write wrapper with optional delegated-owner context kept narrow

**Rationale**: The local tool inventory records `comments.setModerationStatus` as `oauth_required`, and nearby write wrappers surface that requirement directly in metadata, docstrings, and review artifacts. YT-119 should follow the same pattern so maintainers can tell before implementation review that public-only access is unsupported. Optional delegated-owner context may remain visible if the wrapper chooses to expose it, but it should not widen the supported moderation-state contract beyond what this slice documents. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/auth.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/research.md`

**Alternatives considered**:

- Model the wrapper as mixed or conditional auth. Rejected because the seed and tool inventory already identify this path as an authorized moderation write operation.
- Leave auth behavior implicit in tests only. Rejected because maintainers need the access boundary visible in review surfaces and wrapper notes.
- Require only API-key access for moderation changes. Rejected because that would directly conflict with the local inventory and write-wrapper pattern.

## Decision: Keep the supported moderation boundary centered on `published`, `heldForReview`, and `rejected`, with `banAuthor` allowed only alongside `rejected`

**Rationale**: The spec requires supported moderation-state transitions and optional moderation-flag rules to be documented. The smallest concrete contract that satisfies that requirement is to accept one moderation status from the representative moderation states used by the endpoint, keep author-ban behavior explicit as an optional moderation flag, and reject incompatible combinations such as a ban-author request paired with a non-rejection moderation outcome. That produces deterministic validation rules without pretending the wrapper supports every conceivable moderation combination. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`

**Alternatives considered**:

- Avoid naming moderation states and only speak in generic terms. Rejected because the spec explicitly requires moderation-state transitions to be reviewable.
- Allow `banAuthor` with any moderation state. Rejected because it weakens the transition boundary and creates ambiguous moderation intent.
- Add more moderation-specific toggles in this slice. Rejected because the current repo contracts only require moderation status flags generically and the slice should stay narrow.

## Decision: Normalize successful results as moderation acknowledgments instead of full comment resources

**Rationale**: The local tool inventory describes `comments_setModerationStatus` output as a moderation-update acknowledgment payload rather than an updated comment resource. YT-119 should therefore normalize success into an acknowledgment-oriented result that preserves the targeted comment IDs, requested moderation state, optional flag visibility, and source metadata needed by downstream layers, even when the upstream success path returns no response body. This keeps the wrapper aligned with the endpoint's moderation intent and avoids pretending the feature returns a full refreshed comment resource. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`

**Alternatives considered**:

- Return a full comment payload after moderation. Rejected because the local tool inventory describes an acknowledgment-style outcome instead.
- Return only a generic boolean. Rejected because downstream reuse needs the applied moderation state and target context to stay visible.
- Reuse the update-comment result shape. Rejected because moderation acknowledgments and comment edits are distinct user intents and should remain reviewably different.

## Decision: Preserve explicit failure boundaries between invalid request shapes, auth mismatches, unsupported moderation transitions, and normalized upstream moderation failures

**Rationale**: The YT-119 spec requires downstream callers to distinguish invalid moderation payloads from missing authorization, unsupported moderation combinations, and upstream rejections. Existing write-wrapper planning already separates local validation failures from auth failures and from normalized upstream failures. The smallest useful split is therefore to keep invalid request shapes, auth mismatches, unsupported moderation-transition combinations, and upstream moderation failures reviewable as different outcomes while preserving successful moderation acknowledgments for valid requests. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/contracts/layer1-comments-insert-auth-write-contract.md`

**Alternatives considered**:

- Flatten validation and auth failures into one generic invalid-request outcome. Rejected because caller remediation differs when the moderation payload is malformed versus when authorization is missing.
- Treat unsupported moderation combinations as ordinary upstream failures. Rejected because the wrapper boundary should protect documented local moderation rules before execution.
- Over-specialize local failure categories beyond the feature need. Rejected because one clear split between validation, auth, unsupported-transition, and normalized upstream failures is sufficient for planning.

## Decision: Keep the implementation seam centered on `wrappers.py`, `youtube.py`, `consumer.py`, `__init__.py`, and the existing Layer 1 test suites

**Rationale**: `wrappers.py` already contains the endpoint-specific builder and auth-validation pattern used by nearby write wrappers, `youtube.py` is the transport seam for request construction and normalized response parsing, `consumer.py` already exposes higher-layer summaries for internal wrappers, `__init__.py` exports new wrapper builders, and the existing unit, contract, integration, and transport tests already cover neighboring Layer 1 read and write features with minimal duplication. This is the smallest extension path for one more moderation endpoint slice. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comments_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

**Alternatives considered**:

- Create a new dedicated moderation module for one endpoint slice. Rejected because the repository already has an endpoint-wrapper home and one slice does not justify new architecture.
- Limit validation to metadata-only tests. Rejected because the constitution requires integration and regression coverage.
- Skip higher-layer summary updates. Rejected because neighboring write-wrapper slices already use consumer summaries to prove downstream reviewability.

## Clarification Closure

All planning-time clarifications for YT-119 are resolved in this research artifact. No `NEEDS CLARIFICATION` markers remain.
