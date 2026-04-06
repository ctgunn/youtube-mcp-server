# Research: YT-104 Layer 1 Endpoint `captions.list`

## Decision: Support `videoId` as the primary selector and `id` as an allowed direct caption-track lookup path

**Rationale**: Local repository artifacts already frame `captions.list` around `part`, `videoId`, `id`, and `onBehalfOfContentOwner` in `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`. The YT-104 spec also prioritizes caption tracks associated with a video, so `videoId` should be the main reviewable path, with `id` documented as a narrower direct lookup selector where the wrapper contract explicitly allows it.

**Alternatives considered**:

- Support only `videoId`. Rejected because the local tool inventory already names `id` as part of the near-raw input surface.
- Expose every possible upstream field immediately. Rejected because this slice is meant to establish a reviewable initial wrapper contract, not exhaust the full upstream surface.
- Treat `videoId` and `id` as interchangeable without documenting boundaries. Rejected because later Layer 2 and Layer 3 reuse depends on knowing which selector path is being used.

## Decision: Model `captions.list` as `oauth_required` metadata with explicit delegation notes, not as mixed auth

**Rationale**: The local tool inventory marks `captions.list` as `Auth: oauth_required`, unlike `activities.list`, which is explicitly mixed by filter mode. The existing Layer 1 metadata model already supports a stable auth mode plus maintainer-facing notes, so the smallest fit is `AuthMode.OAUTH_REQUIRED` with a contract note that `onBehalfOfContentOwner` is an optional delegation input rather than a separate auth mode.

**Alternatives considered**:

- Model `captions.list` as `mixed/conditional`. Rejected because no local artifact indicates a public API-key path for this endpoint.
- Hide delegation details in implementation only. Rejected because the YT-104 spec explicitly requires delegation context to be visible to maintainers before reuse.
- Treat `onBehalfOfContentOwner` as a separate wrapper. Rejected because this feature is scoped to one endpoint-specific Layer 1 wrapper contract.

## Decision: Treat selector choice as explicit and reject unsupported or ambiguous combinations before execution

**Rationale**: The existing `EndpointRequestShape` already supports mutually exclusive selector validation through `exactly_one_of`, and YT-104 explicitly requires unsupported combinations to be rejected or clearly flagged. The wrapper contract should therefore document a deterministic selector boundary instead of passing ambiguous combinations through to upstream behavior.

**Alternatives considered**:

- Forward all combinations upstream and rely on upstream validation. Rejected because that makes the internal contract unclear to later consumers.
- Silently prioritize one selector over another. Rejected because it hides caller intent and weakens contract reviewability.

## Decision: Treat empty valid caption lists as successful outcomes, not wrapper failures

**Rationale**: The YT-104 spec states that absence of caption tracks must not be treated as failure. That matches the existing Layer 1 pattern used in YT-103, where valid empty collections remain on the success path and only normalized upstream failures are treated as errors.

**Alternatives considered**:

- Convert no-caption results into a wrapper-specific error. Rejected because no tracks found is a valid business outcome.
- Add a special empty-result mode outside the normal success path. Rejected because the current executor/result split is already sufficient.

## Decision: Implement YT-104 by extending the current Layer 1 foundation modules and tests

**Rationale**: The repo already has the minimal seam needed for this slice in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/auth.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and the Layer 1 test files under `/Users/ctgunn/Projects/youtube-mcp-server/tests/`. The live upstream gap can be closed by adding `captions.list` behavior through the existing executor and transport seam rather than replacing it.

**Alternatives considered**:

- Introduce a dedicated `captions.py` integration module immediately. Rejected for planning because the current representative wrapper pattern is the smallest implementation path for one endpoint-specific slice.
- Replace the representative wrapper pattern with a broader endpoint registry. Rejected because YT-104 is a single-endpoint slice and the current seam already supports it.
- Add public tool or protocol changes in YT-104. Rejected because this slice is internal-only and later Layer 2 or Layer 3 exposure belongs to separate work.

## Decision: Use the existing Layer 1 unit, integration, transport, and contract suites as the minimum test surface

**Rationale**: `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py` is already the place where endpoint-specific wrapper metadata, selector validation, and auth-mode behavior are asserted. `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py` already covers wrapper execution through the shared executor and empty-result success behavior. `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py` already validates request construction and HTTP transport behavior against the live YouTube endpoint shape. A dedicated feature-local captions contract suite can mirror the YT-103 pattern without widening generic metadata tests, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py` can verify that higher-layer summaries preserve quota, auth, and delegation visibility.

**Alternatives considered**:

- Put all YT-104 checks into generic metadata contract tests only. Rejected because endpoint-specific selector and delegation rules are better protected by a feature-local contract test.
- Rely only on unit tests. Rejected because the constitution requires integration and regression coverage across contract boundaries.

## Decision: Use two feature-local contract artifacts to guide later transcript and caption reuse

**Rationale**: YT-104 needs one contract focused on wrapper identity, quota cost `50`, request-shape visibility, and internal-only scope, and a second contract focused on OAuth-required access, `videoId` versus `id` selector expectations, `onBehalfOfContentOwner` delegation handling, invalid-combination rules, and empty-result semantics. This split matches the current YT-103 pattern and gives later transcript and caption slices a stable artifact to reuse.

**Alternatives considered**:

- Keep all design guidance only in the implementation plan. Rejected because later tasking and reuse need stable contract artifacts.
- Keep all design guidance in one contract file. Rejected because auth, delegation, and selector semantics are important enough for this endpoint to deserve a dedicated reusable artifact.
