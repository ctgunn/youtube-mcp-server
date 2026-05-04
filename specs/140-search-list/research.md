# Research: YT-140 Layer 1 Endpoint `search.list`

## Decision: Support one deterministic search request shape with required `part` and `q`

**Rationale**: Repository-local metadata tests already use `search` as the representative high-cost list endpoint with `required_fields=("part", "q")`, and the Layer 2 tool inventory also treats `q` as a core search input. Keeping `part` and `q` required gives YT-140 a stable, reviewable base contract that still aligns with the shared `EndpointRequestShape` pattern used by other list wrappers. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/spec.md`

**Alternatives considered**:

- Make `q` optional for special search modes. Rejected because the repository-local metadata examples for `search` already require `q`, and the feature spec consistently describes a normal search-query contract rather than a selector-less special case.
- Require only `q`. Rejected because the existing Layer 1 list-wrapper pattern keeps `part` explicit in metadata and validation.
- Allow a loosely shaped search payload and defer field requirements to transport code. Rejected because the shared request-shape contract exists specifically to make boundaries reviewable before execution.

## Decision: Expose the near-raw search filter catalog from the local tool inventory, while keeping the seed-mandated refinement categories central in wrapper notes

**Rationale**: The local Layer 2 tool specification already enumerates the intended `search.list` filter catalog: `channelId`, `forContentOwner`, `forDeveloper`, `forMine`, `publishedAfter`, `publishedBefore`, `regionCode`, `relevanceLanguage`, `safeSearch`, `type`, `videoCaption`, `videoDefinition`, `videoDuration`, `videoEmbeddable`, `videoLicense`, `videoPaidProductPlacement`, `videoSyndicated`, `videoType`, `order`, `pageToken`, and `maxResults`. YT-140 specifically calls out search type, pagination, date filtering, and language or region refinements, so the wrapper contract should keep those categories especially visible while still staying close to the near-raw endpoint surface expected by the repository. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/PRD.md`

**Alternatives considered**:

- Limit the optional field catalog only to `type`, `pageToken`, `maxResults`, `publishedAfter`, `publishedBefore`, `regionCode`, and `relevanceLanguage`. Rejected because the local Layer 2 tool inventory already defines a broader near-raw search surface.
- Promise every undocumented upstream filter automatically. Rejected because the plan should stay anchored to repository-local artifacts rather than speculative upstream coverage.
- Hide the optional field catalog in code only. Rejected because maintainers need a reviewable contract before implementation.

## Decision: Treat search type as a first-class refinement and reject incompatible video-only combinations when the request is not scoped to video search

**Rationale**: The seed explicitly requires search-type handling to be documented, and the local tool inventory groups several video-specific filters under `search.list`. The smallest defensible interpretation is to keep `type` reviewable and require endpoint-specific validation to reject combinations where a video-only refinement is supplied on a search path that does not support it. This matches the repository's existing preference for deterministic validation over silent coercion. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`

**Alternatives considered**:

- Ignore search-type interactions and allow all documented filters together. Rejected because it would make the contract ambiguous and weaken failure reviewability.
- Keep `type` undocumented in the wrapper and rely on downstream tools to infer compatibility. Rejected because the seed requires search-type behavior to be visible in the wrapper contract.
- Restrict YT-140 to one fixed search type. Rejected because the local requirements describe `search.list` as a reusable endpoint wrapper, not a single-purpose higher-level query.

## Decision: Preserve upstream-style pagination through `pageToken` and `maxResults` rather than remapping or defaulting it inside the Layer 1 contract

**Rationale**: Local tool guidance says Layer 2 and upstream-facing layers should preserve upstream pagination concepts where practical, and the feature spec explicitly calls out pagination for YT-140. The existing Layer 1 list wrappers also expose `pageToken` and `maxResults` directly in request-shape metadata rather than hiding them behind server-side defaults. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/PRD.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/spec.md`

**Alternatives considered**:

- Remap pagination to a different internal name such as `pageSize`. Rejected because Layer 1 stays close to upstream request parameters.
- Omit pagination from the wrapper contract and let later layers add it. Rejected because YT-140 explicitly includes pagination in scope.
- Impose Layer 3 defaults such as `maxResults=10` inside the Layer 1 contract. Rejected because those are public-tool conventions, not the correct default planning boundary for a near-raw internal wrapper.

## Decision: Support `publishedAfter` and `publishedBefore` as the reviewable date-filter pair and keep them aligned to the repository's ISO 8601 conventions

**Rationale**: Both the common tool conventions and the YT-140 seed explicitly call out date filtering. The repository standard says these filters must accept ISO 8601 timestamps, so YT-140 should treat the pair as the canonical date-scoping path for the wrapper contract and keep invalid or incomplete date combinations reviewable. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/spec.md`

**Alternatives considered**:

- Leave date filtering unspecified until implementation. Rejected because Phase 0 must close planning-time contract questions.
- Support only one bound. Rejected because the local requirements describe date filtering broadly enough that the maintainers need both narrowing fields visible.
- Treat date filtering as a Layer 3 concern only. Rejected because YT-140 explicitly scopes it into the Layer 1 wrapper contract.

## Decision: Support `regionCode` and `relevanceLanguage` as the reviewable language or region refinement pair for this slice

**Rationale**: The seed explicitly calls out language and region refinements, and the local `search.list` tool inventory names `regionCode` and `relevanceLanguage` as the near-raw upstream fields that provide those behaviors. Keeping those names visible in the wrapper contract also aligns with the repository's practice of preserving upstream naming in Layer 1. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/spec.md`

**Alternatives considered**:

- Rename the fields to higher-level public names inside Layer 1. Rejected because Layer 1 stays close to upstream request semantics.
- Use transcript-style `language` handling. Rejected because the local transcript conventions are a different feature area and the `search.list` inventory already names the correct upstream fields.
- Leave region or language scoping implicit in notes only. Rejected because the feature spec requires those refinements to be documented in the wrapper contract.

## Decision: Model `search.list` as `AuthMode.CONDITIONAL`, with API key as the default public path and OAuth only for restricted filters

**Rationale**: The Layer 2 inventory describes `search.list` as API-key based, but the repository's own metadata standards and integration tests already use `search` as the representative example of a mixed or conditional-auth endpoint with an explicit `auth_condition_note`. That combination is best reconciled by treating public query search as the default API-key path while documenting restricted filters such as `forContentOwner`, `forDeveloper`, and `forMine` as conditional-auth cases that require stronger authorization. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/auth.py`

**Alternatives considered**:

- Model `search.list` as API-key only. Rejected because repository-local metadata tests already require conditional-auth review surfaces for `search`.
- Model `search.list` as OAuth-only. Rejected because the local tool inventory and existing examples both preserve public search as a valid path.
- Leave auth behavior implicit in tests only. Rejected because maintainers need the access boundary visible in review surfaces and wrapper notes.

## Decision: Keep the official quota cost `100` highly visible in metadata, docstrings, consumer summaries, and feature-local contracts

**Rationale**: The seed requires the official quota cost of `100` to appear in method metadata and comments or docstrings, and the PRD explicitly names `search.list` as one of the highest-impact quota methods that must be especially visible in Layer 1 documentation and implementation notes. The repository's metadata-review and consumer-summary patterns already provide the right surfaces for that visibility. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/PRD.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Alternatives considered**:

- Keep quota only in tests or feature planning docs. Rejected because the seed requires maintainer-visible wrapper-level quota documentation.
- Rely on external docs for quota awareness. Rejected because the repository requires quota visibility inside local artifacts.

## Decision: Use the existing `inconsistent-docs` lifecycle state and a caveat note to represent the known search quota guidance inconsistency

**Rationale**: The current Layer 1 metadata tests already use `search` as the canonical example of a wrapper with `lifecycle_state="inconsistent-docs"` and the caveat note that official quota guidance differs between public overview and endpoint reference pages. Reusing that pattern keeps YT-140 aligned with the standards already encoded in the repository instead of inventing a new caveat model. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/102-layer1-metadata-standards/contracts/layer1-reviewability-contract.md`

**Alternatives considered**:

- Ignore the quota inconsistency and show only `100` with no caveat. Rejected because the current metadata standards already require the caveat to remain visible for `search`.
- Create a search-specific caveat mechanism. Rejected because the repository already has a general lifecycle and caveat model.
- Treat the inconsistency as an implementation-only note. Rejected because the reviewability contract says caveat type and implication must be visible to maintainers.

## Decision: Preserve explicit boundaries between invalid request shapes, restricted-auth failures, empty-result success, and normalized upstream search failures

**Rationale**: YT-140 requires downstream callers to distinguish malformed requests, incompatible refinements, requests that need stronger authorization, valid empty searches, and genuine upstream failures. The existing integration layer already separates local validation from normalized upstream failures, and nearby list wrappers preserve empty results as successful no-match outcomes. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`

**Alternatives considered**:

- Flatten empty results and failures into one generic unsuccessful outcome. Rejected because downstream remediation differs substantially.
- Treat all conditional-auth requests as unsupported rather than restricted. Rejected because the repository already models mixed or conditional auth explicitly.
- Add a much broader failure taxonomy now. Rejected because the spec only requires clear separation of the major outcome types.

## Decision: Keep the implementation seam centered on `wrappers.py`, `youtube.py`, `consumer.py`, `__init__.py`, and the existing Layer 1 metadata, integration, and transport tests

**Rationale**: `wrappers.py` already contains the endpoint-specific metadata and notes pattern used by neighboring list wrappers, `youtube.py` is the transport seam for request construction and response parsing, `consumer.py` already exposes higher-layer summaries that surface source metadata, `__init__.py` exports endpoint builders, and the existing unit, contract, integration, and transport tests already contain `search` metadata examples that can be converted into endpoint-specific coverage with minimal structural churn. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

**Alternatives considered**:

- Create a new search-specific integration submodule for one endpoint slice. Rejected because one wrapper does not justify new architecture.
- Limit validation to metadata-only checks. Rejected because the constitution requires integration and regression coverage.
- Skip consumer-summary updates. Rejected because the spec expects maintainer-visible reuse guidance beyond raw transport details.

## Decision: Use two feature-local contracts mirroring the existing wrapper-plus-auth-behavior pattern

**Rationale**: Nearby endpoint slices separate wrapper-level metadata requirements from more specific auth or behavior guidance. Reusing that split for YT-140 keeps one contract focused on wrapper identity, quota visibility, and request shape, and a second focused on conditional-auth behavior, refinement compatibility, empty-result handling, and failure interpretation. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/139-playlists-delete/contracts/layer1-playlists-delete-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/139-playlists-delete/contracts/layer1-playlists-delete-auth-delete-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/spec.md`

**Alternatives considered**:

- Use one contract file only. Rejected because wrapper requirements and refinement or auth behavior become harder to review cleanly together.
- Put all guidance in the plan and skip feature-local contracts. Rejected because the constitution requires contract-first design artifacts.
- Create a larger multi-endpoint search contract now. Rejected because this slice should stay scoped to one endpoint.

## Clarification Closure

All planning-time clarifications for YT-140 are resolved in this research artifact. No `NEEDS CLARIFICATION` markers remain.
