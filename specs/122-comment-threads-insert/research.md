# Research: YT-122 Layer 1 Endpoint `commentThreads.insert`

## Decision: Support one deterministic video-targeted top-level thread-creation shape using `part` plus a comment-thread `body`

**Rationale**: The local feature spec defines YT-122 around top-level comment-thread creation, not generic comment-thread writes. The smallest request contract that satisfies the seed is therefore one required `part` field plus one required `body` payload that expresses a new top-level comment thread for one supported discussion target. For implementation, this slice chooses one video-targeted profile through `body.snippet.videoId` plus `body.snippet.topLevelComment.snippet.textOriginal` rather than multiple target modes. Existing internal write-wrapper precedent uses deterministic endpoint-specific validation rather than permissive pass-through behavior. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/122-comment-threads-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`

**Alternatives considered**:

- Support all possible upstream comment-thread create shapes in this slice. Rejected because the seed only requires top-level thread creation and widening the contract would dilute one endpoint-slice delivery.
- Treat the request body as opaque pass-through JSON. Rejected because nearby Layer 1 write wrappers validate supported body shapes before execution.
- Support multiple target profiles immediately. Rejected because the local spec only requires one supported discussion target and the repository precedent favors one narrow deterministic create profile per slice.

## Decision: Model `commentThreads.insert` as an OAuth-required write wrapper with limited optional delegation review guidance

**Rationale**: The local tool inventory records `commentThreads.insert` as `oauth_required`, and nearby write wrappers surface that requirement directly in metadata, docstrings, and review artifacts. YT-122 should follow the same pattern so maintainers can tell before implementation review that public-only access is unsupported. For this slice, the smallest supported extra write context is optional `onBehalfOfContentOwner` review guidance, which can remain visible without widening the supported top-level thread-create body contract. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/auth.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/research.md`

**Alternatives considered**:

- Model the wrapper as mixed or conditional auth. Rejected because the seed and tool inventory already identify this path as an authorized write operation.
- Introduce multiple delegation fields by default. Rejected because adjacent comment write/delete slices intentionally keep delegation narrow to optional `onBehalfOfContentOwner` guidance.
- Leave auth behavior implicit in tests only. Rejected because maintainers need the access boundary visible in review surfaces and wrapper notes.

## Decision: Keep the supported create boundary centered on video-targeted top-level comment-thread creation and reject reply-style or mixed create shapes

**Rationale**: The YT-122 seed explicitly calls out top-level-comment creation behavior. The local specification also scopes this slice to top-level thread creation, not replies. The smallest consistent approach is to require a top-level comment-thread body through `body.snippet.videoId` and `body.snippet.topLevelComment.snippet.textOriginal`, then reject create requests that imply reply creation, omit the required top-level content, or introduce unrelated write modes. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/122-comment-threads-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/research.md`

**Alternatives considered**:

- Support both top-level thread creation and replies in YT-122. Rejected because YT-122 explicitly scopes to top-level creation and YT-117 already covers reply creation.
- Infer create mode from any nested fields that resemble thread or reply content. Rejected because silent interpretation would make reuse and failure analysis harder.
- Allow unsupported extra body fields for forward compatibility. Rejected because current Layer 1 wrappers reject undocumented fields by design.

## Decision: Make quota cost `50`, OAuth requirement, top-level-only boundaries, and delegation guidance visible in metadata, docstrings, and contract artifacts

**Rationale**: The seed requires the official quota cost of `50` to be recorded in metadata and method comments or docstrings, and the specification requires top-level creation behavior and authorization expectations to be reviewable. Existing Layer 1 slices keep quota, auth behavior, and request boundaries discoverable through wrapper metadata, feature-local contracts, higher-layer summary surfaces, and tests. YT-122 should follow that pattern for consistency and downstream planning reuse. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/122-comment-threads-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/contracts/layer1-comments-insert-wrapper-contract.md`

**Alternatives considered**:

- Keep quota and top-level-create guidance only in planning docs. Rejected because the seed requires metadata and docstring visibility.
- Put auth and boundary guidance only in tests. Rejected because higher-layer authors need reviewable contracts before reading code.
- Keep unsupported-shape handling implicit in runtime exceptions. Rejected because later layers need deterministic, documented boundaries.

## Decision: Preserve explicit failure boundaries between invalid request shapes, auth mismatches, target-eligibility failures, and normalized upstream write failures

**Rationale**: The YT-122 spec requires downstream callers to distinguish invalid top-level create requests from missing authorization or ineligible creation targets. Existing write-wrapper planning already separates local validation failures from auth failures and from normalized upstream failures. The smallest useful split is therefore to keep invalid request shapes, auth mismatches, target-eligibility failures, and upstream create failures reviewable as different outcomes while preserving successful created-thread handling for valid requests. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/122-comment-threads-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`

**Alternatives considered**:

- Flatten validation and auth failures into one generic invalid-request outcome. Rejected because caller remediation differs when the body is malformed versus when authorization is missing.
- Flatten target-ineligibility into generic upstream or validation failures. Rejected because the feature spec explicitly requires a distinct target-eligibility boundary for planning and remediation.
- Over-specialize local failure categories beyond the feature need. Rejected because one clear split between validation, auth, target-eligibility, and normalized upstream failures is sufficient for planning.

## Decision: Keep the implementation seam centered on `wrappers.py`, `youtube.py`, `consumer.py`, `__init__.py`, and the existing Layer 1 test suites

**Rationale**: `wrappers.py` already contains the endpoint-specific builder and auth-validation pattern used by nearby write wrappers, `youtube.py` is the transport seam for request construction and normalized response parsing, `consumer.py` already exposes higher-layer summaries for internal wrappers, and the existing unit, contract, integration, and transport tests already cover neighboring Layer 1 read and write features with minimal duplication. This is the smallest extension path for one more write endpoint slice. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comment_threads_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

**Alternatives considered**:

- Create a new dedicated comment-thread create module for one endpoint slice. Rejected because the repository already has an endpoint-wrapper home and one slice does not justify new architecture.
- Limit implementation to `wrappers.py` plus docs/tests, with no `youtube.py` changes. Rejected because create responses and normalized upstream error categories for a new operation are handled in `youtube.py`.
- Skip higher-layer summary updates entirely. Viable, but weaker against the repo’s current Layer 1 pattern where write wrappers usually get a higher-layer summary and matching contract coverage.

## Clarification Closure

All planning-time clarifications for YT-122 are resolved in this research artifact. No `NEEDS CLARIFICATION` markers remain.
