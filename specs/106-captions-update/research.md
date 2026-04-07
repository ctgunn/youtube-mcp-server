# Research: YT-106 Layer 1 Endpoint `captions.update`

## Decision: Require `part` plus `body` in every supported `captions.update` request and treat `media` as an explicit optional body-plus-media content-replacement path

**Rationale**: The local tool inventory defines `captions.update` as taking a caption resource update body plus media-upload inputs when required, not as an upload-only endpoint. The current transport code already supports both JSON body-only updates and multipart body-plus-media updates for `PUT` operations, so the smallest consistent contract is to require `body` on every update request and allow `media` only when caption content replacement is part of the requested body-plus-media update path.

**Alternatives considered**:

- Require `media` for every update request. Rejected because the local tool inventory says media-upload inputs are only required when needed, and the current transport already supports body-only update requests.
- Allow `media` without `body`. Rejected because YT-106 requires the wrapper to identify the caption being updated and reject incomplete update shapes before execution.
- Model separate metadata-only and content-replacement wrappers. Rejected because the existing Layer 1 pattern keeps one wrapper per endpoint slice.

## Decision: Keep the request shape deterministic and reject unsupported body/media combinations before execution

**Rationale**: The current Layer 1 contract model already enforces required fields, rejects unexpected fields, and supports endpoint-specific validators. YT-106 explicitly calls for unsupported or ambiguous update combinations to be rejected or clearly flagged. The clean fit is to define a narrow allowed field set and validate it in the wrapper contract before the executor runs.

**Alternatives considered**:

- Forward loosely shaped requests upstream and document caveats only in markdown. Rejected because the repo's existing wrapper pattern uses `EndpointRequestShape.validate_arguments()` to make boundaries enforceable.
- Silently coerce incomplete requests into a supported shape. Rejected because that weakens the Layer 1 contract and makes later Layer 2 and Layer 3 reuse ambiguous.
- Accept arbitrary extra fields for future compatibility. Rejected because the current Layer 1 foundation rejects unexpected fields by design.

## Decision: Treat media-update expectations as part of the wrapper contract, not a transport-only detail

**Rationale**: YT-106 acceptance criteria call out media-update behavior as wrapper-contract material, and adjacent captions work in YT-104 and YT-105 keeps auth, selector, and upload semantics visible in wrapper metadata and contract artifacts before implementation details are inspected. For YT-106, update semantics should be equally reviewable so higher layers know whether they need a body-only update or a body-plus-media replacement flow before reusing the wrapper.

**Alternatives considered**:

- Hide media-update rules inside transport code or executor logic. Rejected because maintainers are supposed to understand the contract before reading implementation.
- Put media-update guidance only in tests. Rejected because tests prove behavior but do not provide the intended maintainer-facing contract surface.
- Split media-update semantics into a separate wrapper. Rejected because YT-106 is scoped to one endpoint-specific Layer 1 wrapper.

## Decision: Model `captions.update` as `oauth_required`, not mixed or public

**Rationale**: The local tool inventory explicitly marks `captions_update` as `Auth: oauth_required`, and the Layer 1 standards require each wrapper to record auth mode in metadata for downstream reuse. Nothing in the repo suggests an API-key path for this endpoint, so the smallest consistent fit is `AuthMode.OAUTH_REQUIRED`.

**Alternatives considered**:

- Mixed or conditional auth. Rejected because no local artifact indicates selector-dependent public access.
- API-key auth. Rejected because the local tool inventory explicitly says `oauth_required`.

## Decision: Treat content-owner delegation as reviewable input guidance, not as a separate auth mode or separate wrapper

**Rationale**: The existing captions precedent in YT-104 and YT-105 models `onBehalfOfContentOwner` as optional delegation context attached to an OAuth-required wrapper. That is the smallest consistent fit for YT-106 as well: base auth remains OAuth-required while delegation stays visible in notes and contracts for higher-layer authors.

**Alternatives considered**:

- Separate delegated wrapper. Rejected because the repo's current Layer 1 pattern keeps one wrapper per endpoint slice.
- Hide delegation in implementation only. Rejected because later layers need to see delegation expectations before reuse.
- Ignore delegation entirely. Rejected because the YT-106 spec already requires maintainers to understand any supported delegation context before reuse.

## Decision: Make quota cost `450` especially visible in metadata, docstrings, and contract artifacts

**Rationale**: The PRD calls out `captions.update` as one of the highest-impact quota methods and requires quota cost to be recorded in wrapper metadata and in docstrings or adjacent comments. The current Layer 1 review surface already exposes `quotaCost`, and higher-layer consumer summaries already propagate source quota data, so YT-106 should use the same visibility pattern.

**Alternatives considered**:

- Keep quota only in tests or planning docs. Rejected because the PRD requires maintainer-visible wrapper-level quota documentation.
- Rely on external docs for quota awareness. Rejected because the repo requires quota visibility inside repository artifacts.

## Decision: Preserve a maintainer-facing review surface that exposes endpoint identity, auth mode, quota, and delegation notes before higher-layer reuse

**Rationale**: The existing `EndpointMetadata.review_surface()` already exposes `resourceName`, `operationName`, `operationKey`, `quotaCost`, `authMode`, and `notes`. The current consumer summaries also preserve source operation, auth mode, quota cost, and notes for captions work, so YT-106 should preserve that review surface and extend its notes for metadata-versus-media update behavior.

**Alternatives considered**:

- Runtime-only enforcement with no review artifact. Rejected because the repo's planning and contract tests require reviewable metadata.
- Contract markdown only without a programmatic review surface. Rejected because existing code and tests already depend on programmatic metadata review.

## Decision: Implement YT-106 by extending the current Layer 1 foundation modules and existing Layer 1-focused tests

**Rationale**: The repo already has the minimal seam needed for this slice in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/auth.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and the Layer 1 test files under `/Users/ctgunn/Projects/youtube-mcp-server/tests/`. The live upstream gap can be closed by adding `captions.update` behavior through the existing representative wrapper and executor seam rather than replacing it.

**Alternatives considered**:

- Introduce a dedicated `captions.py` integration module immediately. Rejected for planning because the current representative wrapper pattern is the smallest implementation path for one endpoint-specific slice.
- Replace the representative wrapper pattern with a broader endpoint registry. Rejected because YT-106 is a single-endpoint slice and the current seam already supports it.
- Add public tool or protocol changes in YT-106. Rejected because this slice is internal-only and later Layer 2 or Layer 3 exposure belongs to separate work.

## Decision: Keep the code-change seam centered on `wrappers.py`, `youtube.py`, and `consumer.py`, with tests mirrored across the existing Layer 1 unit, integration, transport, and caption-focused contract suites

**Rationale**: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` already holds endpoint-specific wrapper classes and builder functions, so YT-106 should add `CaptionsUpdateWrapper` and `build_captions_update_wrapper()` there. `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py` is already the request-builder seam and can support both JSON `PUT` updates and multipart `PUT` updates with small endpoint-local additions. `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py` is the smallest place to add higher-layer review summaries that preserve source quota and notes for update flows. The minimum regression surface follows the current caption pattern in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`.

**Alternatives considered**:

- Put YT-106-specific request semantics in generic metadata classes. Rejected because that would broaden the abstraction instead of keeping the change endpoint-local.
- Use only unit tests. Rejected because the constitution requires integration and regression coverage across contract boundaries.
- Put YT-106 assertions into generic metadata contract tests only. Rejected because media-update and authorization guidance are endpoint-specific and belong in a caption-focused contract suite.
