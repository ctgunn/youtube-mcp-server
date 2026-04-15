# Research: YT-117 Layer 1 Endpoint `comments.insert`

## Decision: Support one deterministic reply-creation shape using `part` plus a comment `body`

**Rationale**: The local feature spec defines YT-117 around reply creation, not generic comment creation. The smallest request contract that satisfies the seed is therefore one required `part` field plus one required `body` payload that expresses a reply to an existing parent comment. Existing internal write-wrapper precedent uses deterministic request shapes with endpoint-specific validation rather than permissive pass-through behavior. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`

**Alternatives considered**:

- Support all possible upstream comment-create shapes in this slice. Rejected because the seed only requires reply-creation behavior and widening the contract would dilute one endpoint-slice delivery.
- Treat the request body as opaque pass-through JSON. Rejected because nearby Layer 1 write wrappers validate supported body shapes before execution.
- Allow requests without a `body` when higher layers already know the target comment. Rejected because current Layer 1 write wrappers require the full supported create payload at the wrapper boundary.

## Decision: Model `comments.insert` as an OAuth-required write wrapper with limited optional delegation review guidance

**Rationale**: The local tool inventory records `comments.insert` as `oauth_required`, and nearby write wrappers surface that requirement directly in metadata, docstrings, and review artifacts. YT-117 should follow the same pattern so maintainers can tell before implementation review that public-only access is unsupported. For this slice, the smallest supported extra write context is optional `onBehalfOfContentOwner` review guidance, which can remain visible without widening the supported reply-create body contract. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/auth.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/research.md`

**Alternatives considered**:

- Model the wrapper as mixed or conditional auth. Rejected because the seed and tool inventory already identify this path as an authorized write operation.
- Leave auth behavior implicit in tests only. Rejected because maintainers need the access boundary visible in review surfaces and wrapper notes.
- Require only API-key access for replies. Rejected because that would directly conflict with the local inventory and write-wrapper pattern.

## Decision: Keep the supported create boundary centered on `body.snippet.parentId` plus `body.snippet.textOriginal` and reject unsupported top-level or mixed create shapes

**Rationale**: The YT-117 seed explicitly calls out reply-creation behavior. The local specification also scopes this slice to reply creation, parent-comment targeting, and failure clarity for unsupported shapes. The smallest consistent approach is to require a reply payload through `body.snippet.parentId` and `body.snippet.textOriginal`, then reject create requests that imply top-level comment creation, omit one of those required fields, or introduce unrelated write modes. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`

**Alternatives considered**:

- Support both reply creation and top-level comment creation now. Rejected because the feature specification bounds the slice to reply creation and clear unsupported-shape handling.
- Infer reply mode from any nested fields that resemble a parent relationship. Rejected because silent interpretation would make reuse and failure analysis harder.
- Allow extra unsupported body fields for forward compatibility. Rejected because current Layer 1 wrappers reject undocumented fields by design.

## Decision: Make quota cost `50`, OAuth requirement, reply boundary, and unsupported-shape guidance visible in metadata, docstrings, and contract artifacts

**Rationale**: The seed requires the official quota cost of `50` to be recorded in metadata and method comments or docstrings, and the specification requires reply behavior and authorization expectations to be reviewable. Existing Layer 1 slices keep quota, auth behavior, and request boundaries discoverable through wrapper metadata, feature-local contracts, higher-layer summary surfaces, and tests. YT-117 should follow that pattern for consistency and downstream planning reuse. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/contracts/layer1-channel-sections-insert-wrapper-contract.md`

**Alternatives considered**:

- Keep quota and reply guidance only in planning docs. Rejected because the seed requires metadata and docstring visibility.
- Put reply-boundary guidance only in tests. Rejected because higher-layer authors need reviewable contracts before reading code.
- Keep unsupported-shape handling implicit in runtime exceptions. Rejected because later layers need deterministic, documented boundaries.

## Decision: Preserve explicit failure boundaries between invalid request shapes, auth mismatches, and normalized upstream write failures

**Rationale**: The YT-117 spec requires downstream callers to distinguish invalid reply payloads from missing authorization and upstream rejections. Existing write-wrapper planning already separates local validation failures from auth failures and from normalized upstream failures. The smallest useful split is therefore to keep invalid request shapes, auth mismatches, and upstream write failures reviewable as different outcomes while preserving successful created-comment handling for valid requests. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/contracts/layer1-channel-sections-insert-auth-write-contract.md`

**Alternatives considered**:

- Flatten validation and auth failures into one generic invalid-request outcome. Rejected because caller remediation differs when the body is malformed versus when authorization is missing.
- Treat upstream rejections as equivalent to local validation errors. Rejected because higher layers need to know whether to retry, escalate access, or correct input.
- Over-specialize local failure categories beyond the feature need. Rejected because one clear split between validation, auth, and normalized upstream failures is sufficient for planning.

## Decision: Keep the implementation seam centered on `wrappers.py`, `youtube.py`, `consumer.py`, and the existing Layer 1 test suites

**Rationale**: `wrappers.py` already contains the endpoint-specific builder and auth-validation pattern used by nearby write wrappers, `youtube.py` is the transport seam for request construction and normalized response parsing, `consumer.py` already exposes higher-layer summaries for internal wrappers, and the existing unit, contract, integration, and transport tests already cover neighboring Layer 1 read and write features with minimal duplication. This is the smallest extension path for one more write endpoint slice. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comments_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

**Alternatives considered**:

- Create a new dedicated comments-create module for one endpoint slice. Rejected because the repository already has an endpoint-wrapper home and one slice does not justify new architecture.
- Limit validation to metadata-only tests. Rejected because the constitution requires integration and regression coverage.
- Skip higher-layer summary updates. Rejected because nearby write-wrapper slices already use consumer summaries to prove downstream reviewability.

## Clarification Closure

All planning-time clarifications for YT-117 are resolved in this research artifact. No `NEEDS CLARIFICATION` markers remain.
