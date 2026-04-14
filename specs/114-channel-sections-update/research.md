# Research: YT-114 Layer 1 Endpoint `channelSections.update`

## Decision: Model `channelSections.update` as an OAuth-required write wrapper with one deterministic `part` plus `body` request shape

**Rationale**: The local feature spec defines YT-114 as an internal Layer 1 wrapper for the real `PUT /channelSections` write path, and nearby write-wrapper precedents already use required `part` and `body` fields for deterministic update behavior. Keeping the update boundary in one wrapper with a stable `body` payload fits the existing Layer 1 contract model used by `channels.update` and `channelSections.insert`. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/114-channel-sections-update/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/111-channels-update-wrapper/research.md`

**Alternatives considered**:

- Treat `channelSections.update` as mixed or conditional auth. Rejected because the existing write-wrapper pattern does not describe a public update path for channel-section mutation.
- Allow loosely shaped update inputs without a stable `body` field. Rejected because the current Layer 1 write wrappers keep update contracts deterministic and reviewable.
- Split updates into multiple wrapper variants by section type. Rejected because the repository pattern remains one wrapper per endpoint slice.

## Decision: Require the update body to include the existing channel-section identity and limit supported body fields to reviewable writable areas

**Rationale**: YT-114 specifically calls for safe updates that clearly identify the target section and reject unsupported fields. The `channels.update` pattern already requires `body.id` and rejects unsupported fields before execution, and the `channelSections.insert` pattern narrows writeable content to `snippet` and `contentDetails`. The smallest consistent fit for YT-114 is to require `body.id`, allow only update-relevant section fields such as `snippet` and `contentDetails`, and reject read-only or extraneous fields before execution. This is an inference from the repository’s established write-wrapper conventions rather than a quoted upstream contract. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/114-channel-sections-update/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/111-channels-update-wrapper/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/data-model.md`

**Alternatives considered**:

- Treat any field returned by the upstream resource as tentatively writable. Rejected because the spec requires clear unsupported-update boundaries.
- Require only `body.id` and defer all other validation to the upstream API. Rejected because downstream callers need deterministic Layer 1 validation boundaries.
- Encode the target section identity outside `body`. Rejected because existing update-wrapper patterns keep resource identity in the request body.

## Decision: Reuse the section-type and reference-alignment rules from `channelSections.insert` for update validation, with update-specific identity requirements layered on top

**Rationale**: The current repository already contains maintainable rules for playlist-backed and channel-backed channel-section types, including title requirements and duplicate-reference rejection. Reusing those rules for update requests preserves consistency between create and update behavior, reduces duplicated logic, and keeps higher-layer expectations stable. YT-114 only needs to extend that model with explicit target-section identity and unsupported-update handling. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/contracts/layer1-channel-sections-insert-wrapper-contract.md`

**Alternatives considered**:

- Treat update validation as a completely separate rule set from create validation. Rejected because it would duplicate section-type semantics already modeled in-repo.
- Allow section types to change without revalidating title and content reference rules. Rejected because it weakens the deterministic contract promised by the spec.
- Collapse all section types into one generic update schema. Rejected because playlist-backed and channel-backed sections have materially different required fields.

## Decision: Preserve OAuth-required behavior and optional content-owner delegation as reviewable metadata on the wrapper contract

**Rationale**: Neighboring write wrappers already make OAuth-required behavior and optional delegation inputs visible in metadata notes and contract artifacts. YT-114 benefits from the same approach because callers need to know both that owner-authorized access is mandatory and that supported partner-style delegation inputs can accompany an authorized request. This keeps authorization expectations visible without broadening the feature into a separate identity or partner-management workflow. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/spec.md`

**Alternatives considered**:

- Hide delegation support inside code only. Rejected because maintainers need reviewable contract guidance before reuse.
- Omit delegation guidance entirely. Rejected because nearby write-wrapper patterns already expose supported optional owner context.
- Treat delegation inputs as required. Rejected because the current Layer 1 patterns describe them as optional authorized-request context.

## Decision: Keep failure boundaries distinct for authorization, invalid update shape, unsupported-update attempts, and normalized upstream write failures

**Rationale**: The YT-114 spec explicitly requires downstream callers to distinguish invalid update shapes from missing owner authorization and unsupported field changes. Existing Layer 1 write-slice planning also treats failure-boundary clarity as part of the public contract for higher-layer reuse. The smallest useful split is to keep auth failures, invalid update requests, unsupported local boundaries, and normalized upstream failures separate. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/114-channel-sections-update/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/111-channels-update-wrapper/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/research.md`

**Alternatives considered**:

- Flatten all update failures into one generic invalid-request outcome. Rejected because caller remediation differs between auth, shape, and unsupported-write problems.
- Treat unsupported update boundaries as upstream-only failures. Rejected because the wrapper contract must make local boundaries explicit before execution.
- Over-specialize failure categories beyond the feature need. Rejected because the smallest reliable split is enough for higher-layer recovery choices.

## Decision: Keep the implementation seam centered on the existing wrapper, transport, consumer, and contract test modules

**Rationale**: The current repository already routes endpoint-specific wrapper work through `wrappers.py`, `youtube.py`, optional consumer summaries, and focused unit, contract, integration, and transport tests. Reusing that seam is the simplest path for YT-114 and aligns with the neighboring YT-111 and YT-113 slices. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_sections_contract.py`

**Alternatives considered**:

- Create a new dedicated module just for channel-sections update orchestration. Rejected because one endpoint slice does not justify new architecture.
- Limit validation to metadata-only tests. Rejected because the constitution requires integration and regression coverage.
- Skip consumer and transport touch points. Rejected because the existing Layer 1 slices use those seams to prove end-to-end internal reuse.

## Clarification Closure

All planning-time clarifications for YT-114 are resolved in this research artifact. No `NEEDS CLARIFICATION` markers remain.
