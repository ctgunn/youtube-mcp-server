# Research: YT-142 Layer 1 Endpoint `subscriptions.insert`

## Decision: Require one stable writable `snippet` payload in the minimum `subscriptions.insert` request contract

**Rationale**: The local feature seed commits to a real `subscriptions.insert` wrapper and explicitly calls out OAuth and writable-part requirements. For this endpoint, the smallest reviewable contract is one required `part` field plus one required `body` payload containing a writable `snippet` section, rather than a looser contract that leaves required create data implicit. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`

**Alternatives considered**:

- Allow part-free requests and rely on upstream rejection. Rejected because YT-142 requires deterministic contract boundaries before execution.
- Split create inputs across multiple top-level fields beyond a stable body payload. Rejected because neighboring mutation wrappers use one reviewable mapping field for write payloads.
- Treat writable-part support as an implementation-only detail. Rejected because maintainers must understand the create boundary before reading code.

## Decision: Model `subscriptions.insert` as OAuth-required with the official quota cost of `50`

**Rationale**: The endpoint is a write operation and the seed explicitly requires OAuth and quota visibility to be documented. The narrowest consistent contract is therefore an `oauth_required` wrapper with official quota cost `50`, visible in wrapper metadata, docstrings, consumer summaries, and feature-local contracts. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`

**Alternatives considered**:

- Mixed or conditional auth. Rejected because the feature scope centers on one write path, not a mixed-auth contract.
- API-key auth. Rejected because this slice is explicitly mutation-oriented and the seed requires OAuth guidance.
- Keep quota only in planning docs. Rejected because the seed requires quota visibility in method metadata and maintainer-facing artifacts.

## Decision: Require `body.snippet.resourceId.channelId` as the minimum supported target-subscription data

**Rationale**: The feature specification centers on creating a subscription relationship through a stable internal wrapper and requires the minimum target-subscription details to be reviewable. The smallest deterministic request shape is a writable `body.snippet.resourceId` mapping that carries the target `channelId`, with the wrapper keeping that required target visible to higher layers and reviewers. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`

**Alternatives considered**:

- Require only a generic writable body and let the wrapper infer which nested fields matter. Rejected because inferred target state would weaken the Layer 1 contract.
- Support every possible upstream create field in the initial slice. Rejected because the repository's Layer 1 planning pattern favors a smaller reviewable contract per endpoint.
- Accept partially populated target-subscription data and defer missing-field handling to the transport. Rejected because current wrapper planning keeps invalid shapes out of executor flow.

## Decision: Treat `body.snippet.resourceId.kind` as optional but constrained to `youtube#channel` when provided

**Rationale**: Neighboring insert wrappers already use nested `resourceId` validation to keep a canonical target type visible while allowing omission when the wrapper can preserve a stable default interpretation. Applying the same pattern here keeps the create boundary explicit without making the minimum request larger than necessary. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/spec.md`

**Alternatives considered**:

- Require `kind` on every request. Rejected because the target channel identity is the core required value, and requiring `kind` would add ceremony without improving the contract boundary materially.
- Ignore `kind` entirely. Rejected because reviewers need a deterministic rule for unsupported target-resource types.
- Support multiple `kind` values in this slice. Rejected because the feature is about one subscription-creation path, not generalized resource targeting.

## Decision: Keep optional writable fields outside the minimum guaranteed contract unless explicitly documented as supported

**Rationale**: The YT-142 spec says supported creation behavior centers on the writable part plus the minimum target-subscription details needed to create the relationship, while optional mutation attributes remain in scope only when the wrapper explicitly documents them. The smallest stable plan is therefore to center the initial contract on `part=snippet`, `body`, `body.snippet.resourceId.channelId`, and the optional constrained `kind`, then require any support for other writable fields to be deliberate and reviewable. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/spec.md`

**Alternatives considered**:

- Promise support for other writable snippet fields immediately. Rejected because it would broaden validation and failure-surface scope without being required by the current feature.
- Leave optional-field behavior unresolved until implementation. Rejected because Phase 0 must close planning-time contract questions.
- Silently ignore unsupported optional fields. Rejected because downstream callers need explicit unsupported-boundary behavior.

## Decision: Keep request validation deterministic and reject unsupported field combinations before execution

**Rationale**: The current Layer 1 contract model already enforces required fields, rejects unexpected fields, and supports endpoint-specific validators. YT-142 explicitly requires missing writable data, unsupported writable parts, and malformed or ineligible target-subscription details to fail clearly. The clean fit is to define a narrow allowed field set and validate it in the wrapper contract before the executor runs. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/spec.md`

**Alternatives considered**:

- Forward loosely shaped requests upstream and document caveats only in markdown. Rejected because the repo's existing wrapper pattern uses `EndpointRequestShape.validate_arguments()` to make boundaries enforceable.
- Silently coerce incomplete requests into a supported shape. Rejected because that would make higher-layer reuse ambiguous.
- Accept arbitrary extra fields for future compatibility. Rejected because the Layer 1 foundation rejects unexpected fields by design.

## Decision: Preserve explicit boundaries between invalid request shapes, access failures, duplicate or ineligible target failures, normalized upstream create failures, and successful creation outcomes

**Rationale**: The YT-142 spec requires downstream callers to distinguish malformed requests, missing OAuth access, unsupported writable boundaries, and validly shaped authorized requests that still fail upstream because the target relationship already exists or cannot be created. The smallest consistent approach is to preserve separate normalized failure categories such as `invalid_request`, access-related failure, and upstream create rejection while keeping successful creation outcomes distinct. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`

**Alternatives considered**:

- Flatten malformed requests and upstream rejections into one generic failure bucket. Rejected because caller remediation differs depending on whether the request is incomplete, unauthorized, or rejected after execution.
- Treat all validly shaped authorized requests as success regardless of upstream outcome. Rejected because that would erase meaningful failure boundaries required by the spec.
- Add a broader failure taxonomy at planning time. Rejected because the spec does not require extra categories beyond clear separation of the major outcome types.

## Decision: Expose required create inputs on higher-layer subscription-create summaries

**Rationale**: YT-142 requires maintainers to confirm quota, OAuth expectations, and minimum create inputs without reading transport code. The most direct higher-layer review surface is therefore a subscription-create summary that echoes the wrapper's required fields, the active writable part, and the required nested target-channel field alongside quota and auth metadata. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Alternatives considered**:

- Keep required-input guidance only in markdown artifacts. Rejected because later layers would lose the quick review surface that the spec asks for.
- Expose raw request bodies in summaries. Rejected because the summary should stay stable and review-oriented rather than mirror request internals wholesale.
- Add a new metadata abstraction just for one endpoint. Rejected because the existing consumer summary shape already supports small contract-focused additions.

## Decision: Keep the implementation seam centered on `wrappers.py`, `youtube.py`, `consumer.py`, `__init__.py`, and the existing Layer 1 test suites

**Rationale**: `wrappers.py` already contains the endpoint-specific metadata and validation pattern used by neighboring mutation wrappers, `youtube.py` is the transport seam for request construction and normalized response parsing, `consumer.py` already exposes higher-layer summaries that surface source metadata, `__init__.py` exports endpoint builders, and the existing unit, contract, integration, and transport tests cover adjacent create-oriented Layer 1 slices with minimal duplication. This is the smallest extension path for one OAuth-required subscription creation endpoint. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_subscriptions_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

**Alternatives considered**:

- Create a new subscriptions integration submodule for one endpoint slice. Rejected because one wrapper does not justify new architecture.
- Limit validation to metadata-only checks. Rejected because the constitution requires integration and regression coverage.
- Skip consumer-summary updates. Rejected because the spec expects maintainer-visible reuse guidance beyond raw transport details.

## Decision: Use two feature-local contracts separating wrapper identity from auth and writable-boundary guidance

**Rationale**: Nearby mutation-oriented Layer 1 slices separate wrapper-level metadata requirements from more specific auth and write-boundary guidance. Reusing that split for YT-142 keeps one contract focused on wrapper identity and response expectations and a second focused on required create inputs, OAuth requirements, target-channel validation, optional-field boundaries, and failure interpretation, which will be helpful for later subscription write planning. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/137-playlists-insert/contracts/layer1-playlists-insert-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/137-playlists-insert/contracts/layer1-playlists-insert-auth-write-contract.md`

**Alternatives considered**:

- Use one contract file only. Rejected because wrapper requirements and write-boundary behavior become harder to review cleanly together.
- Put all guidance in the plan and skip feature-local contracts. Rejected because the constitution requires contract-first design artifacts.
- Create a larger multi-endpoint subscriptions contract now. Rejected because this slice should stay scoped to one endpoint.

## Clarification Closure

All planning-time clarifications for YT-142 are resolved in this research artifact. No `NEEDS CLARIFICATION` markers remain.
