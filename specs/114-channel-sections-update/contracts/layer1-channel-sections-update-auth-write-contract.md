# Contract: YT-114 Layer 1 `channelSections.update` Auth and Write Contract

## Purpose

Define how maintainers and future higher-layer authors should interpret `channelSections.update` authorization requirements, writable field rules, section-type alignment guidance, optional delegation behavior, and invalid-update boundaries when reusing the internal Layer 1 wrapper.

The representative implementation for this contract remains under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Authorization Expectations

- `channelSections.update` requires authorized channel-management access
- `channelSections.update` requires OAuth-required access
- public API-key-only update behavior is not part of the supported contract for this slice
- optional `onBehalfOfContentOwner` and `onBehalfOfContentOwnerChannel` inputs may accompany authorized requests when partner-style delegation is supported by the selected caller context
- missing or mismatched authorization must fail distinctly from malformed update bodies

The contract must let maintainers tell, before implementation review, that update access is owner-scoped and not interchangeable with the mixed-auth retrieval path used by `channelSections.list`.

## Supported Write Boundary

The update contract must make these writable expectations reviewable:

- the request must identify the existing section being updated
- supported update bodies stay within the documented writable section areas for this slice
- section-type rules remain explicit for playlist-backed, channel-backed, and other supported channel-section types
- playlist-backed section types must not be paired with unexpected channel reference lists
- channel-backed section types must not be paired with unexpected playlist reference lists
- title-required section types must fail clearly when the title is missing
- duplicated playlist or channel references remain unsupported
- read-only or unsupported fields must fail clearly rather than being ignored silently

The feature does not need to broaden scope into a separate layout-orchestration workflow, bulk-update behavior, or MCP-facing public tool contract.

## Failure Boundary Expectations

Higher layers must be able to distinguish:

- auth failures caused by missing or incompatible authorized access
- local validation failures caused by incomplete update shapes
- unsupported-update failures caused by read-only fields or disallowed writable combinations
- normalized upstream update failures such as ownership, limit, or eligibility issues that survive local validation

The contract must make it clear that unsupported-update boundaries are enforced locally before a request is treated as supported wrapper usage.

## Review Validation Expectations

The feature must prove that maintainers can identify:

- that `channelSections.update` requires OAuth-required access
- that update requests must identify the section being changed
- which section types require playlist IDs, which require channel IDs, and which require neither
- when `snippet.title` is required, optional, or ignored
- that `onBehalfOfContentOwner` and `onBehalfOfContentOwnerChannel` are optional delegation inputs rather than mandatory fields
- that duplicate references, unsupported fields, and malformed update bodies fail differently from auth problems
- that normalized upstream update failures remain distinguishable from local validation failures

Validation must include:

- unit coverage for auth and update-shape validation boundaries
- contract coverage proving review surfaces expose quota, auth, and writable update guidance
- integration coverage showing compatible behavior through the existing executor flow
- transport coverage showing `PUT` request construction for `channelSections.update`

## Invariants

- YT-114 remains internal-only Layer 1 work
- The feature preserves existing Layer 1 metadata and executor abstractions
- Credential material must never appear in docs, tests, or logs
- New or changed Python functions in scope include reStructuredText docstrings
