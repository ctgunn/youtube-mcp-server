# Research: YT-127 Layer 1 Endpoint `membershipsLevels.list`

## Decision: Support one deterministic request shape using required `part`

**Rationale**: The local tool inventory for `membershipsLevels.list` identifies `part` as the stable request input for this endpoint, and the YT-127 spec frames this slice around membership-level retrieval rather than a broad near-raw parameter surface. The smallest stable wrapper contract is therefore one required `part` field with no selector ambiguity, silent fallback behavior, or undocumented optional filters. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/127-memberships-levels-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`

**Alternatives considered**:

- Treat `part` as optional. Rejected because the spec requires a supported retrieval input to remain visible and validated in the wrapper contract.
- Allow broader arbitrary query fields for future flexibility. Rejected because current Layer 1 request shapes reject undocumented inputs by design.
- Support multiple retrieval selectors in one request. Rejected because one deterministic membership-level lookup per request is simpler and matches the current endpoint-slice pattern.

## Decision: Keep optional modifiers out of scope for this slice unless the repo-local contract names them explicitly

**Rationale**: The local tool inventory for `membershipsLevels.list` names only `part`, and the YT-127 spec requires unsupported modifiers to be rejected clearly. The smallest deterministic contract is therefore to document all undocumented filters, paging inputs, and delegation-related fields as unsupported for this slice rather than guessing or broadening the wrapper boundary. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/127-memberships-levels-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`

**Alternatives considered**:

- Add common list-style modifiers such as `pageToken` or `maxResults`. Rejected because those are not part of the in-repo request inventory for this endpoint.
- Accept undocumented modifiers and pass them through. Rejected because undocumented passthrough weakens reviewability and testability.
- Leave modifier support unresolved. Rejected because Phase 0 must close planning decisions without unresolved clarifications.

## Decision: Model `membershipsLevels.list` as an active OAuth-required wrapper with owner-only visibility notes

**Rationale**: The local tool inventory marks `membershipsLevels.list` with `Auth: oauth_required`, and the YT-127 seed explicitly requires OAuth and owner-only visibility requirements to be documented in the wrapper contract. Nothing in the seed or tool inventory indicates mixed or public access for this endpoint. The smallest repo-consistent choice is therefore `auth_mode=oauth_required`, `quota_cost=1`, the standard active lifecycle, and owner-only guidance recorded in wrapper notes and contracts instead of a lifecycle caveat. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/102-layer1-metadata-standards/spec.md`

**Alternatives considered**:

- Use `mixed/conditional` auth. Rejected because the repo-local requirements for `membershipsLevels.list` do not describe a public API-key path.
- Add a reviewable lifecycle caveat. Rejected because the repo-local requirements call out access constraints, not deprecation or limited availability.
- Keep owner-only guidance only in the spec. Rejected because maintainers need the constraint visible in wrapper review surfaces during implementation and reuse.

## Decision: Keep quota cost `1`, OAuth-required access, owner-only visibility, and membership-level guidance visible in metadata, docstrings, consumer summaries, and feature-local contracts

**Rationale**: The YT-127 seed requires the official quota cost of `1` to be recorded in method metadata and method comments or docstrings, and the spec requires maintainers to determine supported inputs, OAuth-required access, and owner-only visibility without reading implementation details. Existing Layer 1 slices keep these decisions discoverable through wrapper metadata, consumer summaries, and feature-local contracts, so YT-127 should follow that same review pattern. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/127-memberships-levels-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Alternatives considered**:

- Keep owner-only guidance only in the plan. Rejected because maintainers and higher-layer authors need the reuse guidance visible in implementation-adjacent review surfaces.
- Omit higher-layer summary coverage. Rejected because nearby Layer 1 slices use consumer summaries to prove reviewable downstream reuse.
- Record auth expectations only in tests. Rejected because reviewable wrapper metadata is the shared repo-local pattern.

## Decision: Preserve explicit boundaries between invalid request shapes, access failures, and successful retrieval outcomes, including empty results

**Rationale**: The YT-127 spec requires downstream callers to distinguish malformed requests from valid owner-scoped membership-level lookups and to distinguish ineligible access from valid empty results. Existing Layer 1 retrieval work already keeps valid empty lists on the success path rather than treating them as failures. The smallest useful split for this endpoint is therefore to keep invalid-request failures and access-related failures explicit while keeping successful retrievals with zero or more items on the success path. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/127-memberships-levels-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/126-members-list/research.md`

**Alternatives considered**:

- Treat empty results as a failure state. Rejected because a valid owner-authorized request with zero returned membership levels is not the same as an invalid request or access failure.
- Flatten empty results and access failures into one generic failure bucket. Rejected because caller remediation differs when the request is malformed, unauthorized, or simply returns no matches.
- Add a more specialized failure taxonomy at planning time. Rejected because the spec does not require additional categories for this slice.

## Decision: Keep the implementation seam centered on `wrappers.py`, `youtube.py`, `consumer.py`, `__init__.py`, and the existing Layer 1 test suites

**Rationale**: `wrappers.py` already contains the endpoint-specific metadata and validation pattern used by neighboring wrappers, `youtube.py` is the transport seam for request construction and normalized response parsing, `consumer.py` already exposes higher-layer summaries that surface source metadata, `__init__.py` exports endpoint builders, and the existing unit, contract, integration, and transport tests cover adjacent Layer 1 retrieval slices with minimal duplication. This is the smallest extension path for one owner-scoped membership-level endpoint. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_memberships_levels_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

**Alternatives considered**:

- Create a new memberships integration submodule for one endpoint slice. Rejected because one wrapper does not justify new architecture.
- Limit validation to metadata-only checks. Rejected because the constitution requires integration and regression coverage.
- Skip consumer-summary updates. Rejected because the spec expects maintainer-visible reuse guidance beyond raw transport details.

## Decision: Use two feature-local contracts mirroring the existing wrapper-plus-behavior pattern

**Rationale**: Nearby Layer 1 slices separate wrapper-level metadata requirements from more specific selector, auth, or behavioral interpretation guidance. Reusing that split for YT-127 keeps one contract focused on wrapper identity and request boundaries and a second focused on owner-only visibility, unsupported modifiers, and empty-result interpretation, which will be helpful for later memberships planning. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/126-members-list/contracts/layer1-members-list-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/126-members-list/contracts/layer1-members-list-owner-visibility-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/125-i18n-regions-list/contracts/layer1-i18n-regions-list-wrapper-contract.md`

**Alternatives considered**:

- Use one contract file only. Rejected because owner-visibility behavior and wrapper requirements become harder to review cleanly together.
- Put all guidance in the plan and skip feature-local contracts. Rejected because the constitution requires contract-first design artifacts.
- Create a larger multi-endpoint memberships contract now. Rejected because this slice should stay scoped to one endpoint.

## Clarification Closure

All planning-time clarifications for YT-127 are resolved in this research artifact. No `NEEDS CLARIFICATION` markers remain.
