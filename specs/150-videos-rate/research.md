# Research: YT-150 Layer 1 Endpoint `videos.rate`

## Decision: Model `videos.rate` as an OAuth-required mutation wrapper with one deterministic `id` plus `rating` request shape

**Rationale**: Local product artifacts already define `videos.rate` as a Layer 1 write endpoint with official quota visibility and documented rating semantics. The local Layer 2 inventory records the near-raw input shape as `id` and `rating`, and the existing Layer 1 mutation-wrapper pattern uses endpoint-specific validation rather than loosely shaped requests. The smallest fit is therefore an OAuth-required wrapper with required `id` plus `rating` fields that stays reviewable and consistent with adjacent mutation endpoints. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`

**Alternatives considered**:

- Treat `videos.rate` as mixed or conditional auth. Rejected because no local artifact indicates a public rating path.
- Rename the target identifier to a new internal-only field such as `videoId`. Rejected because nearby Layer 1 wrappers generally stay close to upstream request naming when the field is already clear.
- Allow arbitrary request mappings without a stable `id` plus `rating` contract. Rejected because existing Layer 1 patterns keep mutation wrappers deterministic and reviewable.

## Decision: Keep the supported rating semantics centered on `like`, `dislike`, and `none`

**Rationale**: The feature specification explicitly requires support for applying a rating and clearing an existing rating. The smallest action set that satisfies those stories and keeps the contract reviewable is `like`, `dislike`, and `none`, with `none` representing the clear-rating path. That gives maintainers one bounded action vocabulary without expanding into unsupported or undocumented rating states. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`

**Alternatives considered**:

- Support only `like` and `dislike`. Rejected because the spec explicitly calls for clearing an existing rating.
- Leave the accepted rating actions implicit until implementation. Rejected because Phase 0 must resolve rating-semantics ambiguity.
- Accept arbitrary rating strings and rely on upstream rejection. Rejected because YT-150 requires deterministic local validation before execution.

## Decision: Treat optional delegation-style or undocumented modifiers as out of scope unless explicitly documented later

**Rationale**: The safest reviewable contract for this slice is one where maintainers can see exactly which request fields are guaranteed: the target identifier and the requested rating action. Keeping optional or delegated modifiers outside the promised contract prevents downstream callers from inferring broader support than the feature requires and keeps the endpoint slice small enough for clear test and contract coverage. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`

**Alternatives considered**:

- Promise support for every upstream modifier immediately. Rejected because it broadens validation and failure-surface scope without being required by the current feature.
- Leave optional-field behavior unresolved until implementation. Rejected because Phase 0 must close planning-time contract questions.
- Silently ignore unsupported fields for forward compatibility. Rejected because higher-layer callers need explicit unsupported-boundary behavior.

## Decision: Keep request validation deterministic and reject unsupported field combinations before execution

**Rationale**: The current Layer 1 contract model already enforces required fields, rejects unexpected fields, and supports endpoint-specific validators. YT-150 explicitly requires missing identifiers, missing rating actions, unsupported rating values, and incompatible auth to fail clearly. The clean fit is to define a narrow allowed field set and validate it in the wrapper contract before the executor runs. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/spec.md`

**Alternatives considered**:

- Forward loosely shaped requests upstream and document caveats only in markdown. Rejected because the repo's existing wrapper pattern uses `EndpointRequestShape.validate_arguments()` to make boundaries enforceable.
- Silently coerce incomplete requests into a supported shape. Rejected because that would make higher-layer reuse ambiguous.
- Accept arbitrary extra fields for future compatibility. Rejected because the Layer 1 foundation rejects unexpected fields by design.

## Decision: Preserve explicit boundaries between invalid request shapes, access failures, normalized upstream rating failures, and successful rating acknowledgements

**Rationale**: The YT-150 spec requires downstream callers to distinguish malformed requests, missing OAuth access, unsupported rating values, and validly shaped authorized requests that still fail upstream because the video is missing, non-ratable, or otherwise ineligible for the mutation. The smallest consistent approach is to preserve separate normalized failure categories such as `invalid_request`, access-related failure, and upstream rating rejection while keeping successful acknowledgement outcomes distinct. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`

**Alternatives considered**:

- Flatten malformed requests and upstream rejections into one generic failure bucket. Rejected because caller remediation differs depending on whether the request is incomplete, unauthorized, or rejected after execution.
- Treat all validly shaped authorized requests as success regardless of upstream outcome. Rejected because that would erase meaningful failure boundaries required by the spec.
- Add a broader failure taxonomy at planning time. Rejected because the spec does not require extra categories beyond clear separation of the major outcome types.

## Decision: Model success as a normalized rating acknowledgement rather than a full refreshed video resource

**Rationale**: The local tool inventory describes the endpoint output as a rating-update acknowledgment payload rather than a refreshed video object. The feature spec also centers on applying or clearing a rating and preserving enough request context for downstream interpretation, which means a lightweight acknowledgement result is the smallest and most accurate success model for this slice. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/spec.md`

**Alternatives considered**:

- Require a follow-up fetch and always return a refreshed video resource. Rejected because the feature does not require extra retrieval fan-out.
- Return only a bare success boolean with no request context. Rejected because downstream layers need to know which video and action the mutation concerned.
- Leave the success shape entirely implicit. Rejected because planning needs a reviewable result boundary.

## Decision: Expose rating-focused higher-layer summary fields for video identity and requested rating action

**Rationale**: YT-150 requires maintainers to confirm quota, OAuth expectations, and rating semantics without reading transport code. The most direct higher-layer review surface is therefore a rating summary that echoes the wrapper's required fields, the target identifier, and the requested rating action alongside quota and auth metadata. This mirrors how neighboring update summaries keep required-input guidance visible for later reuse. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`

**Alternatives considered**:

- Keep required-input guidance only in markdown artifacts. Rejected because later layers would lose the quick review surface that the spec asks for.
- Expose raw transport request details in summaries. Rejected because the summary should stay stable and review-oriented rather than mirror request internals wholesale.
- Reuse the video-update summary unchanged. Rejected because `videos.rate` needs action-oriented semantics instead of writable-body guidance.

## Decision: Keep the implementation seam centered on `wrappers.py`, `youtube.py`, `consumer.py`, `__init__.py`, and the existing Layer 1 video test suites

**Rationale**: `wrappers.py` already contains the endpoint-specific metadata and validation pattern used by neighboring mutation wrappers, `youtube.py` is the transport seam for request construction and normalized response parsing, `consumer.py` already exposes higher-layer summaries that surface source metadata, `__init__.py` exports endpoint builders, and the existing unit, contract, integration, and transport tests cover adjacent video list, video insert, and video update slices with minimal duplication. This is the smallest extension path for one OAuth-required video rating endpoint. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

**Alternatives considered**:

- Create a new videos integration submodule for one endpoint slice. Rejected because one wrapper does not justify new architecture.
- Limit validation to metadata-only checks. Rejected because the constitution requires integration and regression coverage.
- Skip consumer-summary updates. Rejected because the spec expects maintainer-visible reuse guidance beyond raw transport details.

## Decision: Use two feature-local contracts separating wrapper identity from auth and rating-boundary guidance

**Rationale**: Nearby mutation-oriented Layer 1 slices separate wrapper-level metadata requirements from more specific auth and write-boundary guidance. Reusing that split for YT-150 keeps one contract focused on wrapper identity and response expectations and a second focused on required rating inputs, OAuth requirements, supported action boundaries, and failure interpretation, which will be helpful for later video-rating planning. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/149-videos-update/contracts/layer1-videos-update-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/149-videos-update/contracts/layer1-videos-update-auth-write-contract.md`

**Alternatives considered**:

- Use one contract file only. Rejected because wrapper requirements and rating-boundary behavior become harder to review cleanly together.
- Put all guidance in the plan and skip feature-local contracts. Rejected because the constitution requires contract-first design artifacts.
- Create a larger multi-endpoint videos contract now. Rejected because this slice should stay scoped to one endpoint.

## Clarification Closure

All planning-time clarifications for YT-150 are resolved in this research artifact. No `NEEDS CLARIFICATION` markers remain.
