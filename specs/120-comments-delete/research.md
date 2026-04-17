# Research: YT-120 Layer 1 Endpoint `comments.delete`

## Decision: Support one deterministic delete request shape using one required comment identifier with only narrow optional delegation context

**Rationale**: The local feature spec defines YT-120 around deleting one existing comment, not around bulk comment removal or general-purpose comment mutation. The smallest request contract that satisfies the seed is therefore one required `id` field that identifies the target comment for one delete attempt, with only `onBehalfOfContentOwner` considered as optional delegation context if the wrapper chooses to surface it. Existing internal delete-wrapper precedent uses deterministic request shapes with endpoint-specific validation rather than permissive pass-through behavior. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`

**Alternatives considered**:

- Support bulk deletion by allowing multiple comment identifiers in this slice. Rejected because the seed and tool inventory describe one comment identifier and a single deletion acknowledgment payload.
- Treat the request as opaque query pass-through. Rejected because nearby Layer 1 delete and write wrappers validate supported shapes before execution.
- Surface multiple optional delegation fields by default. Rejected because the smallest consistent comment-slice contract is to keep delegation narrow unless the endpoint-specific need is already established.

## Decision: Model `comments.delete` as an OAuth-required destructive wrapper with reviewable authorization notes

**Rationale**: The local tool inventory records `comments.delete` as `oauth_required`, and nearby destructive wrappers surface that requirement directly in metadata, docstrings, and review artifacts. YT-120 should follow the same pattern so maintainers can tell before implementation review that public-only access is unsupported. Optional delegated-owner guidance may remain visible if the wrapper surfaces it, but it should not widen the supported delete boundary beyond what this slice documents. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/auth.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/research.md`

**Alternatives considered**:

- Model the wrapper as mixed or conditional auth. Rejected because the seed and tool inventory already identify this path as an authorized delete operation.
- Leave auth behavior implicit in tests only. Rejected because maintainers need the access boundary visible in review surfaces and wrapper notes.
- Require only API-key access for comment deletion. Rejected because that would directly conflict with the local inventory and delete-wrapper pattern.

## Decision: Normalize successful results as deletion acknowledgments instead of refreshed comment resources

**Rationale**: The local tool inventory describes `comments_delete` output as a deletion acknowledgment payload rather than a refreshed comment resource. YT-120 should therefore normalize success into a lightweight delete result that preserves the targeted comment ID, deletion status, optional delegation visibility, and source metadata needed by downstream layers, even when the upstream success path returns no response body. This keeps the wrapper aligned with the endpoint's delete intent and avoids pretending the feature returns a full comment resource after removal. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`

**Alternatives considered**:

- Return a full comment payload after deletion. Rejected because the local tool inventory describes an acknowledgment-style outcome instead.
- Return only a generic boolean. Rejected because downstream reuse needs the targeted comment identity and delete status to remain visible.
- Reuse the moderation-acknowledgment result shape directly. Rejected because moderation and deletion are distinct user intents and should remain reviewably different.

## Decision: Make quota cost `50`, OAuth requirement, delete preconditions, and destructive-operation guidance visible in metadata, docstrings, and contract artifacts

**Rationale**: The seed requires the official quota cost of `50` to be recorded in metadata and method comments or docstrings, and the specification requires OAuth requirements and delete preconditions to be reviewable. Existing Layer 1 slices keep quota, auth behavior, and request boundaries discoverable through wrapper metadata, feature-local contracts, higher-layer summary surfaces, and tests. YT-120 should follow that pattern for consistency and downstream planning reuse. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/contracts/layer1-channel-sections-delete-wrapper-contract.md`

**Alternatives considered**:

- Keep quota and delete guidance only in planning docs. Rejected because the seed requires metadata and docstring visibility.
- Put delete guidance only in tests. Rejected because higher-layer authors need reviewable contracts before reading code.
- Keep unavailable-target handling implicit in runtime exceptions. Rejected because later layers need deterministic, documented boundaries.

## Decision: Preserve explicit failure boundaries between invalid request shapes, auth mismatches, target-state failures, and normalized upstream delete failures

**Rationale**: The YT-120 spec requires downstream callers to distinguish invalid delete requests from missing authorization or ineligible targets when deletion cannot proceed. Existing delete-wrapper planning already separates local validation failures from auth failures and from normalized upstream failures. The smallest useful split is therefore to keep invalid request shapes, auth mismatches, target-state failures, and upstream delete failures reviewable as different outcomes while preserving successful deletion acknowledgments for valid requests. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/contracts/layer1-channel-sections-delete-auth-delete-contract.md`

**Alternatives considered**:

- Flatten validation and auth failures into one generic invalid-request outcome. Rejected because caller remediation differs when the delete target is malformed versus when authorization is missing.
- Treat unavailable targets as ordinary upstream ambiguity. Rejected because the wrapper boundary should make target-state failures reviewable for downstream planning.
- Over-specialize local failure categories beyond the feature need. Rejected because one clear split between validation, auth, target-state, and normalized upstream failures is sufficient for planning.

## Decision: Keep the implementation seam centered on `wrappers.py`, `youtube.py`, `consumer.py`, `__init__.py`, and the existing Layer 1 test suites

**Rationale**: `wrappers.py` already contains the endpoint-specific builder and auth-validation pattern used by nearby write and delete wrappers, `youtube.py` is the transport seam for request construction and normalized response parsing, `consumer.py` already exposes higher-layer summaries for internal wrappers, `__init__.py` exports new wrapper builders, and the existing unit, contract, integration, and transport tests already cover neighboring Layer 1 read, write, moderation, and delete features with minimal duplication. This is the smallest extension path for one more comment endpoint slice. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comments_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

**Alternatives considered**:

- Create a new dedicated comments-delete module for one endpoint slice. Rejected because the repository already has an endpoint-wrapper home and one slice does not justify new architecture.
- Limit validation to metadata-only tests. Rejected because the constitution requires integration and regression coverage.
- Skip higher-layer summary updates. Rejected because nearby delete and moderation slices already use consumer summaries to prove downstream reviewability.

## Clarification Closure

All planning-time clarifications for YT-120 are resolved in this research artifact. No `NEEDS CLARIFICATION` markers remain.
