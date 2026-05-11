# Research: YT-148 Layer 1 Endpoint `videos.insert`

## Decision: Require one stable metadata field plus one stable media-upload field in the minimum `videos.insert` request contract

**Rationale**: The local feature spec and tool inventory both define `videos.insert` as a creation endpoint that needs metadata plus upload content. The smallest reviewable contract is one that requires `part`, one `body` metadata payload, and one `media` upload payload rather than trying to support metadata-only creation or transport-hidden upload behavior.

**Alternatives considered**:

- Allow metadata-only requests and rely on upstream rejection. Rejected because YT-148 explicitly requires media-upload requirements to be documented and invalid request shapes to be rejected before execution.
- Split metadata submission and upload submission into separate wrapper contracts. Rejected because the current Layer 1 pattern keeps one wrapper per endpoint slice and the tool inventory describes one `videos.insert` operation.
- Model every possible upstream field in the initial contract. Rejected because adjacent Layer 1 slices use a smaller deterministic request boundary first.

## Decision: Keep the request shape deterministic and reject unsupported combinations before execution

**Rationale**: The current Layer 1 contract model already enforces required fields, rejects unexpected fields, and supports endpoint-specific validators. YT-148 calls for missing required metadata, missing upload content, unsupported upload-mode combinations, and invalid access context to be distinguished clearly before expensive execution begins.

**Alternatives considered**:

- Forward loosely shaped requests upstream and document caveats only in markdown. Rejected because the repo's wrapper pattern uses `EndpointRequestShape.validate_arguments()` to make request boundaries enforceable.
- Silently coerce incomplete requests into a supported shape. Rejected because that weakens the Layer 1 contract and undermines later Layer 2 and Layer 3 reuse.
- Accept arbitrary extra fields for future compatibility. Rejected because the current Layer 1 foundation rejects unexpected fields by design.

## Decision: Model `videos.insert` as an OAuth-required endpoint with no public or API-key-compatible path

**Rationale**: The local tool inventory explicitly marks `videos_insert` as `Auth: oauth_required`, and adjacent upload-sensitive wrappers already make that access mode reviewable in wrapper metadata and docstrings. Nothing in the local project artifacts suggests a supported API-key path for video creation.

**Alternatives considered**:

- Mixed or conditional auth. Rejected because no local artifact indicates a selector-dependent public path for this endpoint.
- API-key auth. Rejected because the local tool inventory explicitly says `oauth_required`.

## Decision: Treat standard upload and resumable upload as reviewable modes within one wrapper contract

**Rationale**: The YT-148 seed requires media-upload and resumable-upload behavior to be documented in the wrapper contract. Existing upload-sensitive slices already keep upload rules in one wrapper rather than splitting them across multiple abstractions, so the clean fit is one `videos.insert` wrapper with visible guidance for both the basic upload path and the resumable path.

**Alternatives considered**:

- Hide upload-mode distinctions inside transport code or executor logic. Rejected because maintainers should be able to understand the contract before reading implementation.
- Create separate wrappers for standard and resumable uploads. Rejected because the existing Layer 1 model stays one wrapper per endpoint and YT-148 is scoped to one endpoint-specific slice.
- Ignore resumable uploads in the initial slice. Rejected because the seed explicitly calls resumable behavior out as part of the acceptance criteria.

## Decision: Keep audit-related or private-default behavior visible as a maintainer-facing caveat, not as a separate auth mode or result type

**Rationale**: The seed explicitly requires audit or private-default behavior to be documented. The existing metadata model already supports reviewable notes and caveats, so the smallest consistent fit is to keep the endpoint OAuth-only while documenting that a valid video-creation request may still produce a created resource whose initial visibility is affected by audit or default-private behavior.

**Alternatives considered**:

- Model audit/private-default as a separate lifecycle state or separate wrapper. Rejected because the feature is still one endpoint-specific wrapper and the current metadata model handles reviewable caveats through notes.
- Treat audit/private-default behavior as a runtime-only transport concern. Rejected because maintainers are supposed to understand these caveats before reuse.
- Treat visibility caveats as an error condition. Rejected because the spec expects a created-video outcome to remain recognizable even when initial visibility is constrained.

## Decision: Keep the 1600-unit quota cost highly visible in wrapper metadata, contracts, consumer summaries, and docstrings

**Rationale**: The PRD and tool inventory both call out `videos.insert` as one of the highest-cost operations in the system. Adjacent upload-sensitive endpoints already keep quota cost visible in metadata, tests, and higher-layer summaries, and YT-148 needs the same visibility because expensive creation calls should be reviewable before execution.

**Alternatives considered**:

- Keep quota only in planning docs or tests. Rejected because the project requires maintainer-visible wrapper-level quota documentation.
- Rely on external YouTube docs for quota awareness. Rejected because the repo explicitly keeps quota visibility inside repository artifacts.

## Decision: Preserve a maintainer-facing review surface that exposes endpoint identity, quota, auth mode, upload guidance, and visibility caveats before higher-layer reuse

**Rationale**: `EndpointMetadata.review_surface()` already exposes the fields maintainers use to review wrapper identity, required fields, auth mode, and quota cost. Adjacent upload-sensitive wrappers and consumer summaries use that same surface to make higher-layer reuse decisions possible without reading raw upstream docs, so YT-148 should preserve and extend that pattern.

**Alternatives considered**:

- Runtime-only enforcement with no review artifact. Rejected because the repo's planning and contract tests require reviewable metadata.
- Contract markdown only without a programmatic review surface. Rejected because existing code and tests already depend on metadata review surfaces and higher-layer summaries.

## Decision: Implement YT-148 by extending the current Layer 1 foundation modules and existing Layer 1-focused tests

**Rationale**: The repo already has the minimum seam needed for this slice in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/auth.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and the Layer 1 test files under `/Users/ctgunn/Projects/youtube-mcp-server/tests/`. Adjacent upload-sensitive endpoints prove the feature can be added by extending those seams rather than introducing a broader abstraction shift.

**Alternatives considered**:

- Introduce a dedicated `videos.py` integration module immediately. Rejected for planning because the current representative wrapper pattern is the smallest implementation path for one endpoint-specific slice.
- Replace the representative wrapper pattern with a broader endpoint registry. Rejected because YT-148 is a single-endpoint slice and the current seam already supports it.
- Add public tool or protocol changes in YT-148. Rejected because this slice is internal-only and later Layer 2 or Layer 3 exposure belongs to separate work.

## Decision: Keep the code-change seam centered on `wrappers.py`, `youtube.py`, and `consumer.py`, with tests mirrored across existing Layer 1 unit, integration, transport, and video-focused contract suites

**Rationale**: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` already holds endpoint-specific wrapper classes and builder functions, so YT-148 should add a `VideosInsertWrapper` and `build_videos_insert_wrapper()` there. `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py` is the concrete request-builder and result-normalization seam and is the smallest place that needs to grow for `POST /videos` with upload-aware request construction. `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py` already carries higher-layer summaries for adjacent upload-sensitive wrappers and should expose the same review surface for created videos. The minimum regression surface follows the current pattern in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`.

**Alternatives considered**:

- Put `videos.insert`-specific request semantics in `executor.py`. Rejected because request-shape-to-HTTP translation already belongs in `youtube.py`.
- Put endpoint-specific validation inside generic metadata classes. Rejected because that would broaden the abstraction instead of keeping the change endpoint-local.
- Use only unit tests. Rejected because the constitution requires integration and regression coverage across contract boundaries.
- Put YT-148 assertions only into generic metadata contract tests. Rejected because upload and visibility guidance are endpoint-specific and belong in the video-focused contract suite too.
