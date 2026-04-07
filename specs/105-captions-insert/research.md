# Research: YT-105 Layer 1 Endpoint `captions.insert`

## Decision: Require one stable metadata field plus one stable media-upload field in the minimum `captions.insert` request contract

**Rationale**: Local artifacts are consistent that `captions.insert` is not a metadata-only endpoint. The feature spec and the tool inventory both define the endpoint as requiring metadata plus media-upload input, so the minimum contract should require one reviewable `body` metadata payload field and one reviewable `media` upload field rather than exposing a metadata-only path.

**Alternatives considered**:

- Allow metadata-only requests and rely on upstream rejection. Rejected because YT-105 explicitly requires media-upload requirements to be documented and invalid shapes to be rejected before execution.
- Model every possible upstream field in the initial contract. Rejected because the existing Layer 1 pattern favors a smaller reviewable contract per endpoint slice.
- Treat upload content as optional for the first slice. Rejected because that would contradict the local tool inventory and the YT-105 spec.

## Decision: Keep the request shape deterministic and reject unsupported combinations before execution

**Rationale**: The current Layer 1 contract model already enforces required fields, rejects unexpected fields, and supports endpoint-specific validators. YT-105 explicitly calls for unsupported metadata-only and upload-only requests to be rejected or clearly flagged. The clean fit is to define a narrow allowed field set and validate it in the wrapper contract before the executor runs.

**Alternatives considered**:

- Forward loosely shaped requests upstream and document caveats only in markdown. Rejected because the repo's existing wrapper pattern uses `EndpointRequestShape.validate_arguments()` to make boundaries enforceable.
- Silently coerce incomplete requests into a supported shape. Rejected because that weakens the Layer 1 contract and makes later Layer 2 and Layer 3 reuse ambiguous.
- Accept arbitrary extra fields for future compatibility. Rejected because the current Layer 1 foundation rejects unexpected fields by design.

## Decision: Treat upload requirements as part of the wrapper contract, not a transport-only detail

**Rationale**: YT-105 acceptance criteria call out media-upload requirements as wrapper-contract material, and the adjacent captions work in YT-104 already keeps auth and selector semantics visible in wrapper metadata and contract artifacts before implementation details are inspected. For YT-105, upload semantics should be equally reviewable so higher layers know they must provide both caption metadata and upload content before reusing the wrapper.

**Alternatives considered**:

- Hide upload requirements inside transport code or executor logic. Rejected because maintainers are supposed to understand the contract before reading implementation.
- Put upload guidance only in tests. Rejected because tests prove behavior but do not provide the intended maintainer-facing contract surface.
- Split upload semantics into a separate wrapper. Rejected because YT-105 is scoped to one endpoint-specific Layer 1 wrapper.

## Decision: Model `captions.insert` as `oauth_required`, not mixed or public

**Rationale**: The local tool inventory explicitly marks `captions_insert` as `Auth: oauth_required`, and the Layer 1 standards require each wrapper to record auth mode in metadata for downstream reuse. Nothing in the repo suggests an API-key path for this endpoint, so the smallest consistent fit is `AuthMode.OAUTH_REQUIRED`.

**Alternatives considered**:

- Mixed or conditional auth. Rejected because no local artifact indicates selector-dependent public access.
- API-key auth. Rejected because the local tool inventory explicitly says `oauth_required`.

## Decision: Treat content-owner delegation as reviewable input guidance, not as a separate auth mode or separate wrapper

**Rationale**: The existing captions precedent in YT-104 models `onBehalfOfContentOwner` as optional delegation context attached to an OAuth-required wrapper. That is the smallest consistent fit for YT-105 as well: base auth remains OAuth-required while delegation stays visible in notes and contracts for higher-layer authors.

**Alternatives considered**:

- Separate delegated wrapper. Rejected because the repo's current Layer 1 pattern keeps one wrapper per endpoint slice.
- Hide delegation in implementation only. Rejected because later layers need to see delegation expectations before reuse.
- Ignore delegation entirely. Rejected because the YT-105 spec already requires maintainers to understand any supported delegation context before reuse.

## Decision: Make quota cost `400` especially visible in metadata, docstrings, and contract artifacts

**Rationale**: The PRD calls out `captions.insert` as one of the highest-impact quota methods and requires quota cost to be recorded in wrapper metadata and in docstrings or adjacent comments. The current Layer 1 review surface already exposes `quotaCost`, and higher-layer consumer summaries already propagate source quota data, so YT-105 should use the same visibility pattern.

**Alternatives considered**:

- Keep quota only in tests or planning docs. Rejected because the PRD requires maintainer-visible wrapper-level quota documentation.
- Rely on external docs for quota awareness. Rejected because the repo requires quota visibility inside repository artifacts.

## Decision: Preserve a maintainer-facing review surface that exposes endpoint identity, auth mode, quota, and delegation notes before higher-layer reuse

**Rationale**: The existing `EndpointMetadata.review_surface()` already exposes `resourceName`, `operationName`, `operationKey`, `quotaCost`, `authMode`, and `notes`. YT-104 also established that higher layers should be able to summarize source operation, auth mode, quota cost, and notes without reading raw upstream docs, so YT-105 should preserve that review surface and expand its notes for upload-sensitive behavior.

**Alternatives considered**:

- Runtime-only enforcement with no review artifact. Rejected because the repo's planning and contract tests require reviewable metadata.
- Contract markdown only without a programmatic review surface. Rejected because existing code and tests already depend on programmatic metadata review.

## Decision: Implement YT-105 by extending the current Layer 1 foundation modules and existing Layer 1-focused tests

**Rationale**: The repo already has the minimal seam needed for this slice in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/auth.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and the Layer 1 test files under `/Users/ctgunn/Projects/youtube-mcp-server/tests/`. The live upstream gap can be closed by adding `captions.insert` behavior through the existing representative wrapper and executor seam rather than replacing it.

**Alternatives considered**:

- Introduce a dedicated `captions.py` integration module immediately. Rejected for planning because the current representative wrapper pattern is the smallest implementation path for one endpoint-specific slice.
- Replace the representative wrapper pattern with a broader endpoint registry. Rejected because YT-105 is a single-endpoint slice and the current seam already supports it.
- Add public tool or protocol changes in YT-105. Rejected because this slice is internal-only and later Layer 2 or Layer 3 exposure belongs to separate work.

## Decision: Keep the code-change seam centered on `wrappers.py` and `youtube.py`, with tests mirrored across the existing Layer 1 unit, integration, transport, and caption-focused contract suites

**Rationale**: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` already holds endpoint-specific wrapper classes and builder functions, so YT-105 should add `CaptionsInsertWrapper` and `build_captions_insert_wrapper()` there. `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py` is the concrete request-builder seam and is the smallest place that needs to grow for `POST /captions` with upload-aware request construction. The minimum regression surface follows the current caption pattern in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, and the caption-focused contract suite under `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/`.

**Alternatives considered**:

- Put upload handling in `executor.py`. Rejected because request-shape-to-HTTP translation already belongs in `youtube.py`.
- Put YT-105-specific request semantics in generic metadata classes. Rejected because that would broaden the abstraction instead of keeping the change endpoint-local.
- Use only unit tests. Rejected because the constitution requires integration and regression coverage across contract boundaries.
- Put YT-105 assertions into generic metadata contract tests only. Rejected because upload and authorization guidance are endpoint-specific and belong in a caption-focused contract suite.
