# Research: YT-118 Layer 1 Endpoint `comments.update`

## Decision: Support one deterministic comment-edit shape using `part` plus a writable comment `body`

**Rationale**: The local feature spec defines YT-118 around editing an existing comment, not around general-purpose comment mutation. The smallest request contract that satisfies the seed is therefore one required `part` field plus one required `body` payload that identifies the target comment and carries the updated writable comment content. Existing internal write-wrapper precedent uses deterministic request shapes with endpoint-specific validation rather than permissive pass-through behavior. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`

**Alternatives considered**:

- Support all possible upstream comment-update shapes in this slice. Rejected because the seed only requires writable-field expectations and widening the contract would dilute one endpoint-slice delivery.
- Treat the request body as opaque pass-through JSON. Rejected because nearby Layer 1 write wrappers validate supported body shapes before execution.
- Allow requests without a comment body when higher layers already know the target comment. Rejected because current Layer 1 write wrappers require the full supported update payload at the wrapper boundary.

## Decision: Model `comments.update` as an OAuth-required write wrapper with any optional owner-delegation guidance kept reviewable but narrow

**Rationale**: The local tool inventory records `comments.update` as `oauth_required`, and nearby write wrappers surface that requirement directly in metadata, docstrings, and review artifacts. YT-118 should follow the same pattern so maintainers can tell before implementation review that public-only access is unsupported. If optional owner-delegation guidance is surfaced for this slice, it should remain limited to reviewable wrapper notes rather than widening the supported edit-body contract. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/auth.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/research.md`

**Alternatives considered**:

- Model the wrapper as mixed or conditional auth. Rejected because the seed and tool inventory already identify this path as an authorized write operation.
- Leave auth behavior implicit in tests only. Rejected because maintainers need the access boundary visible in review surfaces and wrapper notes.
- Require only API-key access for comment edits. Rejected because that would directly conflict with the local inventory and write-wrapper pattern.

## Decision: Keep the supported writable boundary centered on `body.id` plus `body.snippet.textOriginal` and reject edits to read-only or unsupported fields

**Rationale**: The YT-118 seed explicitly calls out writable field expectations. The local specification also scopes this slice to revising existing comment content while rejecting fields outside the documented writable boundary. The smallest consistent approach is to require an update payload through `body.id` and `body.snippet.textOriginal`, then reject requests that omit one of those required fields, attempt to update read-only fields, or introduce unrelated write modes. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`

**Alternatives considered**:

- Support broad comment-snippet replacement with multiple writable fields now. Rejected because the feature specification emphasizes clear writable-field expectations over maximal surface coverage.
- Infer the writable boundary from whatever body fields are present. Rejected because silent interpretation would make reuse and failure analysis harder.
- Allow extra unsupported body fields for forward compatibility. Rejected because current Layer 1 wrappers reject undocumented fields by design.

## Decision: Make quota cost `50`, OAuth requirement, writable-field boundary, and unsupported-field guidance visible in metadata, docstrings, and contract artifacts

**Rationale**: The seed requires the official quota cost of `50` to be recorded in metadata and method comments or docstrings, and the specification requires writable-field expectations to be reviewable. Existing Layer 1 slices keep quota, auth behavior, and request boundaries discoverable through wrapper metadata, feature-local contracts, higher-layer summary surfaces, and tests. YT-118 should follow that pattern for consistency and downstream planning reuse. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/contracts/layer1-comments-insert-wrapper-contract.md`

**Alternatives considered**:

- Keep quota and writable-field guidance only in planning docs. Rejected because the seed requires metadata and docstring visibility.
- Put writable-field guidance only in tests. Rejected because higher-layer authors need reviewable contracts before reading code.
- Keep immutable-field handling implicit in runtime exceptions. Rejected because later layers need deterministic, documented boundaries.

## Decision: Preserve explicit failure boundaries between invalid request shapes, auth mismatches, immutable-field violations, and normalized upstream write failures

**Rationale**: The YT-118 spec requires downstream callers to distinguish invalid comment-edit payloads from missing authorization, immutable-field changes, and upstream rejections. Existing write-wrapper planning already separates local validation failures from auth failures and from normalized upstream failures. The smallest useful split is therefore to keep invalid request shapes, auth mismatches, immutable-field violations, and upstream write failures reviewable as different outcomes while preserving successful updated-comment handling for valid requests. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/contracts/layer1-comments-insert-auth-write-contract.md`

**Alternatives considered**:

- Flatten validation and auth failures into one generic invalid-request outcome. Rejected because caller remediation differs when the body is malformed versus when authorization is missing.
- Treat immutable-field violations as the same as any upstream rejection. Rejected because the wrapper boundary should protect documented local write rules before execution.
- Over-specialize local failure categories beyond the feature need. Rejected because one clear split between validation, auth, immutable-field, and normalized upstream failures is sufficient for planning.

## Decision: Keep the implementation seam centered on `wrappers.py`, `youtube.py`, `consumer.py`, and the existing Layer 1 test suites

**Rationale**: `wrappers.py` already contains the endpoint-specific builder and auth-validation pattern used by nearby write wrappers, `youtube.py` is the transport seam for request construction and normalized response parsing, `consumer.py` already exposes higher-layer summaries for internal wrappers, and the existing unit, contract, integration, and transport tests already cover neighboring Layer 1 read and write features with minimal duplication. This is the smallest extension path for one more write endpoint slice. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comments_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

**Alternatives considered**:

- Create a new dedicated comments-update module for one endpoint slice. Rejected because the repository already has an endpoint-wrapper home and one slice does not justify new architecture.
- Limit validation to metadata-only tests. Rejected because the constitution requires integration and regression coverage.
- Skip higher-layer summary updates. Rejected because nearby write-wrapper slices already use consumer summaries to prove downstream reviewability.

## Clarification Closure

All planning-time clarifications for YT-118 are resolved in this research artifact. No `NEEDS CLARIFICATION` markers remain.
