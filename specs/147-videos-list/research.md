# Research: YT-147 Layer 1 Endpoint `videos.list`

## Decision: Support one deterministic request shape using `part` plus exactly one selector from `id`, `chart`, or `myRating`

**Rationale**: The local tool inventory for `videos.list` names `part`, `id`, `chart`, `myRating`, `pageToken`, `maxResults`, `regionCode`, and `videoCategoryId` as the supported inputs, while the YT-147 spec emphasizes clear selector modes such as `id`, `chart`, and other supported selectors. The smallest contract that preserves the documented inventory and deterministic Layer 1 validation is one required `part` value, exactly one selector from `id`, `chart`, or `myRating`, and optional supporting inputs only when they fit the selected lookup path. This keeps the wrapper broad enough for direct video lookup, chart-based browsing, and caller-rating retrieval without permitting ambiguous multi-selector requests. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/147-videos-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`

**Alternatives considered**:

- Support only `part` plus `id`. Rejected because the seed explicitly calls out `chart` and other supported selectors, and the local inventory includes additional selector paths.
- Treat `chart` and `myRating` as optional refinements instead of selectors. Rejected because each path represents a distinct retrieval mode with different auth and paging expectations.
- Require multiple selectors together. Rejected because that would make request interpretation less deterministic and harder to test.

## Decision: Limit `pageToken` and `maxResults` to collection-style selectors and keep direct `id` lookup single-shot

**Rationale**: The in-repo tool inventory includes paging inputs for `videos.list`, but the repo’s existing list-wrapper pattern only allows paging where collection-style retrieval makes sense. Direct `id` lookup is a single-shot retrieval path, while `chart` and `myRating` represent collection-style views. Limiting `pageToken` and `maxResults` to the collection selectors preserves deterministic request validation and matches the established wrapper approach used by playlist and subscription list endpoints. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/147-videos-list/spec.md`

**Alternatives considered**:

- Allow paging for every selector path. Rejected because it would create review ambiguity and allow collection modifiers on a direct-lookup path.
- Omit paging from this slice entirely. Rejected because `pageToken` and `maxResults` are part of the local tool inventory for `videos.list`.
- Delay paging decisions until implementation. Rejected because the constitution requires contract-first planning.

## Decision: Restrict `regionCode` and `videoCategoryId` to chart-oriented retrieval guidance for this slice

**Rationale**: The local tool inventory includes `regionCode` and `videoCategoryId`, but those inputs make sense as chart-oriented refinements rather than universal modifiers across every selector path. Keeping them attached to the chart lookup profile is the smallest deterministic boundary that lets maintainers understand when regional chart browsing or category-scoped chart review is supported without implying those fields are valid for direct `id` retrieval or `myRating` retrieval. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/147-videos-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`

**Alternatives considered**:

- Allow `regionCode` and `videoCategoryId` with every selector. Rejected because the resulting contract would be harder to explain and easier to misuse.
- Exclude `regionCode` and `videoCategoryId` from this slice. Rejected because the repo-local inventory already documents them as supported `videos.list` inputs.
- Tie `videoCategoryId` to `id` retrieval. Rejected because direct `id` lookup already identifies exact videos and does not need category-scoped browsing semantics.

## Decision: Model `videos.list` as a mixed-auth wrapper with API-key access for `id` and `chart`, and OAuth-required access for `myRating`

**Rationale**: The local tool inventory marks `videos.list` as `api_key or mixed, depending on filter mode`, and the spec expects maintainers to understand when a selector may require different access expectations. Existing Layer 1 patterns represent that situation with `AuthMode.CONDITIONAL` plus an `auth_condition_note`. The smallest repo-consistent choice is therefore a mixed-auth wrapper where public video lookup and chart browsing remain API-key compatible while `myRating` is explicitly treated as an OAuth-required personal retrieval path. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/147-videos-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`

**Alternatives considered**:

- Mark the whole wrapper as API-key only. Rejected because the spec and local inventory already indicate mixed auth depending on selector mode.
- Mark the whole wrapper as OAuth-only. Rejected because that would narrow public selector paths beyond the documented inventory.
- Leave auth behavior implicit in implementation only. Rejected because maintainers need the auth split visible in review surfaces.

## Decision: Keep quota cost `1`, selector rules, mixed-auth guidance, and collection-refinement boundaries visible in metadata, docstrings, consumer summaries, and feature-local contracts

**Rationale**: The YT-147 seed requires the official quota cost of `1` to be recorded in method metadata and method comments or docstrings, and the spec requires maintainers to determine supported selectors and access expectations without reading implementation details. Existing Layer 1 slices keep these decisions discoverable through wrapper metadata, consumer summaries, and feature-local contracts, so YT-147 should follow that same review pattern. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/147-videos-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Alternatives considered**:

- Keep selector and auth guidance only in the spec. Rejected because maintainers and higher-layer authors need the reuse guidance visible in implementation-adjacent review surfaces.
- Omit higher-layer summary coverage. Rejected because nearby Layer 1 slices use consumer summaries to prove reviewable downstream reuse.
- Record mixed-auth expectations only in tests. Rejected because the seed requires metadata and docstring visibility.

## Decision: Preserve explicit boundaries between invalid request shapes and successful retrieval outcomes, including empty results

**Rationale**: The YT-147 spec requires downstream callers to distinguish malformed requests from valid video lookups, and it explicitly treats valid empty results as a separate case from invalid input. Existing Layer 1 retrieval work already keeps valid empty lists on the success path rather than treating them as failures. The smallest useful split for this endpoint is therefore to keep invalid-request failures explicit while keeping successful retrievals with zero or more items on the success path. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/147-videos-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/146-video-categories-list/research.md`

**Alternatives considered**:

- Treat empty results as a failure state. Rejected because a valid request with zero returned items is not the same as an invalid request.
- Flatten empty results and validation failures into a generic failure bucket. Rejected because caller remediation differs when the selector shape is wrong versus when the lookup simply returns no items.
- Add a more specialized failure taxonomy at planning time. Rejected because the spec does not require additional categories for this slice.

## Decision: Keep the implementation seam centered on `wrappers.py`, `youtube.py`, `consumer.py`, `__init__.py`, and the existing Layer 1 test suites, with one new feature-specific contract test module

**Rationale**: `wrappers.py` already contains the endpoint-specific metadata and validation pattern used by neighboring wrappers, `youtube.py` is the transport seam for request construction and normalized response parsing, `consumer.py` already exposes higher-layer summaries that surface source metadata, `__init__.py` exports endpoint builders, and the existing unit, contract, integration, and transport tests cover adjacent Layer 1 retrieval slices with minimal duplication. A dedicated `test_layer1_videos_contract.py` module is the smallest clean place to assert the feature-local contract files for selector and mixed-auth behavior without overloading broader metadata suites. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

**Alternatives considered**:

- Create a new video-utilities integration submodule for one endpoint slice. Rejected because one wrapper does not justify new architecture.
- Limit validation to metadata-only checks. Rejected because the constitution requires integration and regression coverage.
- Reuse only the general metadata contract suite. Rejected because `videos.list` combines selector, auth, and refinement semantics that deserve their own focused contract proof.

## Decision: Use two feature-local contracts mirroring the existing wrapper-plus-behavior pattern

**Rationale**: Nearby Layer 1 slices separate wrapper-level metadata requirements from more specific selector, auth, or behavioral interpretation guidance. Reusing that split for YT-147 keeps one contract focused on wrapper identity and request boundaries and a second focused on selector choice, conditional auth behavior, collection refinements, and empty-result handling, which will be helpful for later direct video lookup and chart-oriented feature planning. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/145-video-abuse-report-reasons/contracts/layer1-video-abuse-report-reasons-list-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/146-video-categories-list/contracts/layer1-video-categories-list-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/147-videos-list/spec.md`

**Alternatives considered**:

- Use one contract file only. Rejected because selector behavior and mixed-auth rules become harder to review cleanly together.
- Put all guidance in the plan and skip feature-local contracts. Rejected because the constitution requires contract-first design artifacts.
- Create a larger multi-endpoint videos contract now. Rejected because this slice should stay scoped to one endpoint.

## Clarification Closure

All planning-time clarifications for YT-147 are resolved in this research artifact. No `NEEDS CLARIFICATION` markers remain.
