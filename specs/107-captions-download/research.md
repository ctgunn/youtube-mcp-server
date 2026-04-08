# Research: YT-107 Layer 1 Endpoint `captions.download`

## Decision: Require a caption track identifier and allow only the documented optional download modifiers

**Rationale**: The local tool inventory defines `captions.download` as taking a caption track identifier plus optional `tfmt`, `tlang`, and delegation flags. The existing Layer 1 pattern already uses `EndpointRequestShape.validate_arguments()` to keep wrapper contracts deterministic, so the smallest consistent contract is one required caption-track identifier plus only the documented optional modifiers.

**Alternatives considered**:

- Allow loosely shaped arbitrary query arguments for future flexibility. Rejected because the current Layer 1 foundation rejects unexpected fields by design.
- Require format or language modifiers on every request. Rejected because the seed and tool specs describe them as optional.
- Support both caption track identifier and video identifier. Rejected because the transcript-source strategy in the PRD distinguishes `captions.list(videoId)` from `captions.download(captionTrackId)`.

## Decision: Model `captions.download` as `oauth_required` with explicit permission-sensitive notes

**Rationale**: The local tool inventory marks `captions_download` as `Auth: oauth_required`, and the PRD states that official transcript access through `captions.download` requires OAuth authorization context for the target caption track. The seed also calls out edit-permission requirements, so the wrapper contract needs maintainer-visible notes that authorized access alone may still be insufficient for some tracks.

**Alternatives considered**:

- Mixed or conditional auth. Rejected because no local artifact describes an API-key or public selector path for this endpoint.
- API-key auth. Rejected because the local tool inventory and transcript-source strategy both require authorized access.
- Runtime-only permission handling without metadata notes. Rejected because later transcript and caption-delivery work needs the boundary to be visible before implementation details are inspected.

## Decision: Treat format conversion and language translation as reviewable contract inputs, not transport-only details

**Rationale**: YT-107 explicitly requires format conversion options and language translation parameters to be documented in the wrapper contract. The existing caption-slice pattern keeps endpoint-specific behavioral notes visible in wrapper metadata and contract artifacts, so `tfmt` and `tlang` should be documented and validated at the wrapper boundary.

**Alternatives considered**:

- Hide `tfmt` and `tlang` inside the request builder only. Rejected because maintainers need to see supported options before reading implementation.
- Document options only in tests. Rejected because tests prove behavior but do not serve as the maintainer-facing contract.
- Split translation and format conversion into separate wrappers. Rejected because the repo's current Layer 1 pattern keeps one wrapper per endpoint slice.

## Decision: Keep delegation as optional input guidance, not a separate auth mode or wrapper

**Rationale**: Existing caption slices model `onBehalfOfContentOwner` as optional delegation context layered on top of OAuth-required access. Reusing that pattern keeps the implementation and documentation consistent while still making delegated behavior visible enough for later reuse.

**Alternatives considered**:

- Create a delegated-download wrapper. Rejected because the current Layer 1 pattern keeps one wrapper per endpoint slice.
- Ignore delegation in YT-107. Rejected because the tool inventory explicitly includes delegation flags where supported.
- Treat delegation as a separate auth mode. Rejected because the repo uses metadata notes rather than new auth enums for that distinction.

## Decision: Preserve a distinct failure boundary between `access-denied` tracks and `not-found` tracks

**Rationale**: The spec requires downstream transcript-oriented work to distinguish access-denied conditions from true caption absence. The current executor pattern already normalizes upstream failures, so the wrapper contract should preserve the distinction rather than flattening all failures into one missing-track outcome.

**Alternatives considered**:

- Treat inaccessible tracks as empty or missing. Rejected because that would mislead transcript workflows.
- Collapse all failures into one generic normalized error category. Rejected because later layers need to make product decisions based on access versus absence.
- Return partial success with warning metadata. Rejected because the current shared executor model already separates success and failure outcomes cleanly.

## Decision: Make quota cost `200` visible in metadata, docstrings, and contract artifacts

**Rationale**: The PRD lists `captions.download` among the highest-impact quota methods and requires especially visible Layer 1 documentation for those methods. The existing `review_surface()` and caption contract tests already emphasize quota visibility, so YT-107 should follow the same pattern.

**Alternatives considered**:

- Keep quota only in planning docs. Rejected because the PRD requires quota visibility inside implementation-facing repository artifacts.
- Rely on external upstream docs for quota review. Rejected because maintainers should not need to leave the repository to understand quota impact.

## Decision: Keep the implementation seam centered on `wrappers.py`, `youtube.py`, and the existing Layer 1 test suites

**Rationale**: `wrappers.py` already contains endpoint-specific wrapper classes and builder functions, `youtube.py` is the request-builder seam that transport tests already exercise for caption endpoints, and the current Layer 1 unit, integration, contract, and transport tests provide the minimum regression surface for one more caption endpoint slice.

**Alternatives considered**:

- Introduce a new endpoint registry or a dedicated caption-download module immediately. Rejected because one endpoint slice does not justify a broader abstraction change.
- Limit validation to unit tests only. Rejected because the constitution requires integration and regression coverage across contract boundaries.
- Defer download-result and access-boundary coverage to later transcript features. Rejected because YT-107 is the foundation those features depend on.

## Decision: Keep higher-layer planning aware of download contract details without expanding YT-107 into a public tool

**Rationale**: The PRD identifies transcript workflows as depending on `captions.download`, and the existing `RepresentativeHigherLayerConsumer` pattern preserves source operation, auth mode, quota cost, and notes for caption-related wrappers. YT-107 should stay internal-only while still making the wrapper contract reviewable enough for later higher-layer reuse.

**Alternatives considered**:

- Add the public `captions_download` MCP tool now. Rejected because YT-207 is the separate Layer 2 slice for that work.
- Keep all higher-layer implications out of the plan. Rejected because the spec and PRD both tie this wrapper to transcript follow-on work.
