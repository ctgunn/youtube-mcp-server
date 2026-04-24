# Research: YT-126 Layer 1 Endpoint `members.list`

## Decision: Support one deterministic request shape using required `part` plus required `mode`

**Rationale**: The local tool inventory for `members.list` identifies `part` and `mode` as the stable request inputs for this endpoint, and the YT-126 spec frames this slice around owner-scoped membership retrieval rather than a broad near-raw parameter surface. The smallest stable wrapper contract is therefore one required `part` field plus one required `mode` field, with no selector ambiguity or silent fallback behavior. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/126-members-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`

**Alternatives considered**:

- Treat `mode` as optional. Rejected because the spec requires successful results to preserve the selected membership retrieval mode for downstream layers.
- Accept multiple membership-view selectors in one request. Rejected because one deterministic membership view per request is simpler and matches the current endpoint-slice pattern.
- Allow broader arbitrary query fields for future flexibility. Rejected because current Layer 1 request shapes reject undocumented inputs by design.

## Decision: Keep paging inputs optional and explicit, but keep all other modifiers out of scope for this slice

**Rationale**: The local tool inventory for `members.list` mentions `pageToken` and `maxResults` in addition to `part` and `mode`, while the YT-126 spec requires unsupported modifiers to be rejected clearly. The smallest repo-consistent choice is to allow paging inputs only when explicitly documented by the wrapper contract and to reject any other undocumented modifiers or top-level fields. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/126-members-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`

**Alternatives considered**:

- Exclude `pageToken` and `maxResults` entirely. Rejected because the in-repo inventory already lists them as the expected list-style inputs for this endpoint.
- Accept undocumented modifiers and pass them through. Rejected because undocumented passthrough weakens reviewability and testability.
- Support additional filtering fields immediately. Rejected because the current repo-local contract does not define them for this slice.

## Decision: Model `members.list` as an active OAuth-required wrapper with owner-only visibility notes

**Rationale**: The local tool inventory marks `members.list` with `Auth: oauth_required`, and the YT-126 seed explicitly requires OAuth and owner-only visibility requirements to be documented in the wrapper contract. Nothing in the seed or tool inventory indicates mixed or public access for this endpoint. The smallest repo-consistent choice is therefore `auth_mode=oauth_required`, `quota_cost=1`, the standard active lifecycle, and owner-only guidance recorded in wrapper notes and contracts instead of a lifecycle caveat. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/102-layer1-metadata-standards/spec.md`

**Alternatives considered**:

- Use `mixed/conditional` auth. Rejected because the repo-local requirements for `members.list` do not describe a public API-key path.
- Add a reviewable lifecycle caveat. Rejected because the repo-local requirements call out access constraints, not deprecation or limited availability.
- Keep owner-only guidance only in the spec. Rejected because maintainers need the constraint visible in wrapper review surfaces during implementation and reuse.

## Decision: Treat delegation-related inputs as out of scope for this slice unless a stable repo-local contract names them explicitly

**Rationale**: The local tool inventory only mentions delegation flags for `members.list` conditionally, and current YT-126 artifacts do not identify a stable delegation field name for this endpoint. The smallest deterministic contract is therefore to document delegation-related inputs as unsupported for this slice and to reject them clearly rather than guessing or broadening the boundary. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/126-members-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/104-captions-list/contracts/layer1-captions-auth-selector-contract.md`

**Alternatives considered**:

- Support unnamed delegation flags generically. Rejected because a stable contract needs explicit field names and behavior.
- Infer delegation behavior from other OAuth endpoints. Rejected because adjacent endpoints use named delegation inputs and YT-126 does not yet provide one.
- Leave delegation unresolved. Rejected because Phase 0 must close planning decisions without unresolved clarifications.

## Decision: Keep quota cost `1`, OAuth-required access, owner-only visibility, and membership-view guidance visible in metadata, docstrings, consumer summaries, and feature-local contracts

**Rationale**: The YT-126 seed requires the official quota cost of `1` to be recorded in method metadata and method comments or docstrings, and the spec requires maintainers to determine supported inputs, OAuth-required access, and owner-only visibility without reading implementation details. Existing Layer 1 slices keep these decisions discoverable through wrapper metadata, consumer summaries, and feature-local contracts, so YT-126 should follow that same review pattern. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/126-members-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Alternatives considered**:

- Keep owner-only guidance only in the plan. Rejected because maintainers and higher-layer authors need the reuse guidance visible in implementation-adjacent review surfaces.
- Omit higher-layer summary coverage. Rejected because nearby Layer 1 slices use consumer summaries to prove reviewable downstream reuse.
- Record auth expectations only in tests. Rejected because reviewable wrapper metadata is the shared repo-local pattern.

## Decision: Preserve explicit boundaries between invalid request shapes, access failures, and successful retrieval outcomes, including empty results

**Rationale**: The YT-126 spec requires downstream callers to distinguish malformed requests from valid owner-scoped membership lookups and to distinguish ineligible access from valid empty results. Existing Layer 1 retrieval work already keeps valid empty lists on the success path rather than treating them as failures. The smallest useful split for this endpoint is therefore to keep invalid-request failures and access-related failures explicit while keeping successful retrievals with zero or more items on the success path. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/126-members-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/research.md`

**Alternatives considered**:

- Treat empty results as a failure state. Rejected because a valid owner-authorized request with zero returned members is not the same as an invalid request or access failure.
- Flatten empty results and access failures into one generic failure bucket. Rejected because caller remediation differs when the request is malformed, unauthorized, or simply returns no matches.
- Add a more specialized failure taxonomy at planning time. Rejected because the spec does not require additional categories for this slice.

## Decision: Keep the implementation seam centered on `wrappers.py`, `youtube.py`, `consumer.py`, `__init__.py`, and the existing Layer 1 test suites

**Rationale**: `wrappers.py` already contains the endpoint-specific metadata and validation pattern used by neighboring wrappers, `youtube.py` is the transport seam for request construction and normalized response parsing, `consumer.py` already exposes higher-layer summaries that surface source metadata, `__init__.py` exports endpoint builders, and the existing unit, contract, integration, and transport tests cover adjacent Layer 1 retrieval slices with minimal duplication. This is the smallest extension path for one owner-scoped list endpoint. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

**Alternatives considered**:

- Create a new memberships integration submodule for one endpoint slice. Rejected because one wrapper does not justify new architecture.
- Limit validation to metadata-only checks. Rejected because the constitution requires integration and regression coverage.
- Skip consumer-summary updates. Rejected because the spec expects maintainer-visible reuse guidance beyond raw transport details.

## Decision: Use two feature-local contracts mirroring the existing wrapper-plus-behavior pattern

**Rationale**: Nearby Layer 1 slices separate wrapper-level metadata requirements from more specific selector, auth, or behavioral interpretation guidance. Reusing that split for YT-126 keeps one contract focused on wrapper identity and request boundaries and a second focused on owner-only visibility, unsupported delegation inputs, and empty-result interpretation, which will be helpful for later membership planning. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/contracts/layer1-comment-threads-list-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/contracts/layer1-channel-sections-delete-auth-delete-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/125-i18n-regions-list/contracts/layer1-i18n-regions-list-wrapper-contract.md`

**Alternatives considered**:

- Use one contract file only. Rejected because owner-visibility behavior and wrapper requirements become harder to review cleanly together.
- Put all guidance in the plan and skip feature-local contracts. Rejected because the constitution requires contract-first design artifacts.
- Create a larger multi-endpoint memberships contract now. Rejected because this slice should stay scoped to one endpoint.

## Clarification Closure

All planning-time clarifications for YT-126 are resolved in this research artifact. No `NEEDS CLARIFICATION` markers remain.
