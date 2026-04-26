# Research: YT-128 Layer 1 Endpoint `playlistImages.list`

## Decision: Support one deterministic request shape using required `part` plus exactly one selector from `playlistId` or `id`

**Rationale**: The official `playlistImages.list` documentation describes `part` as required and requires exactly one filter from `playlistId` or `id`. The in-repo tool inventory also names `part`, `playlistId`, and `id` as the core retrieval inputs for the endpoint. The smallest stable wrapper contract is therefore one required `part` field, exactly one selector from `playlistId` or `id`, and no silent fallback between selector modes. Sources: `https://developers.google.com/youtube/v3/docs/playlistImages/list`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`

**Alternatives considered**:

- Treat `playlistId` or `id` as optional. Rejected because the endpoint contract requires one selector.
- Allow both selectors in the same request. Rejected because selector ambiguity weakens reviewability and conflicts with the official filter contract.
- Support arbitrary undocumented selectors for future flexibility. Rejected because current Layer 1 request shapes reject undocumented inputs by design.

## Decision: Allow paging only within the documented `playlistId` retrieval path

**Rationale**: The official docs describe pagination support for retrieving large result sets, which aligns naturally with playlist-scoped retrieval rather than direct image-ID lookup. The repo-local inventory also mentions paging flags only where supported. The smallest deterministic contract is therefore to support optional `pageToken` and `maxResults` for `playlistId` requests, reject them for `id` requests, and reject undocumented modifiers outside that boundary. Sources: `https://developers.google.com/youtube/v3/docs/playlistImages/list`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/128-playlist-images-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`

**Alternatives considered**:

- Allow paging for both selector modes. Rejected because direct ID lookup does not need list-style paging to stay deterministic.
- Reject all paging to keep the request shape smaller. Rejected because the official endpoint behavior and repo-local inventory both describe paging as part of the supported surface.
- Allow undocumented paging flags to pass through when present. Rejected because undocumented passthrough weakens testability and reviewability.

## Decision: Model `playlistImages.list` as an OAuth-required wrapper for all supported requests

**Rationale**: The official `playlistImages.list` documentation states that the request requires authorization scopes, which makes the endpoint OAuth-gated for supported requests. The repo-local `tool-specs.md` inventory notes broader or mixed access depending on filter mode, but the official endpoint reference is the authoritative source, so the wrapper should use `auth_mode=oauth_required`, `quota_cost=1`, and selector guidance rather than conditional auth notes. Sources: `https://developers.google.com/youtube/v3/docs/playlistImages/list`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`

**Alternatives considered**:

- Use `api_key` auth for all requests. Rejected because the official endpoint reference requires authorization scopes.
- Use `mixed/conditional` auth by selector mode. Rejected because the official reference does not describe a public API-key path for `playlistImages.list`.
- Leave auth behavior unresolved until implementation. Rejected because Phase 0 must close contract questions before planning is complete.

## Decision: Keep quota cost `1`, OAuth requirements, selector rules, and paging boundaries visible in metadata, docstrings, consumer summaries, and feature-local contracts

**Rationale**: The YT-128 seed requires the official quota cost of `1` to be recorded in method metadata and method comments or docstrings, and the spec requires maintainers to determine supported filter modes and OAuth requirements without reading implementation details. Existing Layer 1 slices keep these decisions discoverable through wrapper metadata, higher-layer summaries, and feature-local contracts, so YT-128 should follow that same review pattern. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/128-playlist-images-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Alternatives considered**:

- Keep selector and paging guidance only in the plan. Rejected because maintainers and higher-layer authors need the guidance visible in implementation-adjacent review surfaces.
- Omit higher-layer summary coverage. Rejected because nearby Layer 1 slices use consumer summaries to prove downstream reviewability.
- Record OAuth expectations only in tests. Rejected because reviewable wrapper metadata is the shared repo-local pattern.

## Decision: Preserve explicit boundaries between invalid request shapes, access failures, and successful retrieval outcomes, including empty results

**Rationale**: The YT-128 spec requires downstream callers to distinguish malformed requests from valid playlist-image lookups and to distinguish access failures from valid empty results. Existing Layer 1 retrieval work already keeps valid empty lists on the success path rather than treating them as failures. The smallest useful split for this endpoint is therefore to keep invalid-request failures and access-related failures explicit while keeping successful retrievals with zero or more items on the success path. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/128-playlist-images-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/127-memberships-levels-list/research.md`

**Alternatives considered**:

- Treat empty results as a failure state. Rejected because a valid authorized request with zero returned playlist images is not the same as an invalid request or access failure.
- Flatten empty results and access failures into one generic failure bucket. Rejected because caller remediation differs when the request is malformed, unauthorized, or simply returns no matches.
- Add a more specialized failure taxonomy at planning time. Rejected because the spec does not require additional categories for this slice.

## Decision: Keep the implementation seam centered on `wrappers.py`, `youtube.py`, `consumer.py`, `__init__.py`, and the existing Layer 1 test suites

**Rationale**: `wrappers.py` already contains the endpoint-specific metadata and selector-validation pattern used by neighboring wrappers, `youtube.py` is the transport seam for request construction and normalized response parsing, `consumer.py` already exposes higher-layer summaries that surface source metadata, `__init__.py` exports endpoint builders, and the existing unit, contract, integration, and transport tests cover adjacent Layer 1 retrieval slices with minimal duplication. This is the smallest extension path for one OAuth-required playlist-image endpoint. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

**Alternatives considered**:

- Create a new playlist-images integration submodule for one endpoint slice. Rejected because one wrapper does not justify new architecture.
- Limit validation to metadata-only checks. Rejected because the constitution requires integration and regression coverage.
- Skip consumer-summary updates. Rejected because the spec expects maintainer-visible reuse guidance beyond raw transport details.

## Decision: Use two feature-local contracts mirroring the existing wrapper-plus-behavior pattern

**Rationale**: Nearby Layer 1 slices separate wrapper-level metadata requirements from more specific selector, auth, or behavioral interpretation guidance. Reusing that split for YT-128 keeps one contract focused on wrapper identity and request boundaries and a second focused on selector-specific paging rules, OAuth requirements, unsupported modifiers, and empty-result interpretation, which will be helpful for later playlist-image planning. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/126-members-list/contracts/layer1-members-list-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/127-memberships-levels-list/contracts/layer1-memberships-levels-list-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/128-playlist-images-list/spec.md`

**Alternatives considered**:

- Use one contract file only. Rejected because selector behavior and wrapper requirements become harder to review cleanly together.
- Put all guidance in the plan and skip feature-local contracts. Rejected because the constitution requires contract-first design artifacts.
- Create a larger multi-endpoint playlist-images contract now. Rejected because this slice should stay scoped to one endpoint.

## Clarification Closure

All planning-time clarifications for YT-128 are resolved in this research artifact. No `NEEDS CLARIFICATION` markers remain.
