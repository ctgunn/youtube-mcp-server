# Contract: YT-115 Layer 1 `channelSections.delete` Auth and Delete Contract

## Purpose

Define how maintainers and future higher-layer authors should interpret `channelSections.delete` authorization requirements, supported delete inputs, optional delegation behavior, destructive-operation guidance, and target-state failure boundaries when reusing the internal Layer 1 wrapper.

The representative implementation for this contract remains under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Authorization Expectations

- `channelSections.delete` requires authorized channel-management access
- `channelSections.delete` requires OAuth-required access
- public API-key-only delete behavior is not part of the supported contract for this slice
- optional `onBehalfOfContentOwner` and `onBehalfOfContentOwnerChannel` inputs may accompany authorized requests when partner-style delegation is supported by the selected caller context
- missing or mismatched authorization must fail distinctly from malformed delete requests

The contract must let maintainers tell, before implementation review, that delete access is owner-scoped and not interchangeable with the mixed-auth retrieval path used by `channelSections.list`.

## Supported Delete Boundary

The delete contract must make these destructive-operation expectations reviewable:

- the request must identify the existing section being deleted
- supported requests remain scoped to one delete target at a time
- unsupported top-level inputs must fail clearly rather than being ignored silently
- delegated owner context remains optional rather than mandatory
- the feature does not broaden scope into bulk deletion, layout orchestration, or a public MCP-facing tool contract

## Failure Boundary Expectations

Higher layers must be able to distinguish:

- auth failures caused by missing or incompatible authorized access
- local validation failures caused by incomplete or malformed delete requests
- target-state failures caused by already-removed, unavailable, or inaccessible channel sections
- normalized upstream delete failures that survive local validation

The contract must make it clear that unsupported delete boundaries are enforced locally before a request is treated as supported wrapper usage.

## Review Validation Expectations

The feature must prove that maintainers can identify:

- that `channelSections.delete` requires OAuth-required access
- that delete requests must identify the section being removed
- that `onBehalfOfContentOwner` and `onBehalfOfContentOwnerChannel` are optional delegation inputs rather than mandatory fields
- that malformed delete requests fail differently from auth problems
- that unavailable or inaccessible delete targets remain distinguishable from local validation failures
- that normalized upstream delete failures remain distinguishable from local validation failures

Validation must include:

- unit coverage for auth and delete-shape validation boundaries
- contract coverage proving review surfaces expose quota, auth, and delete guidance
- integration coverage showing compatible behavior through the existing executor flow
- transport coverage showing `DELETE` request construction for `channelSections.delete`

## Invariants

- YT-115 remains internal-only Layer 1 work
- The feature preserves existing Layer 1 metadata, executor, and higher-layer summary abstractions
- Credential material must never appear in docs, tests, or logs
- New or changed Python functions in scope include reStructuredText docstrings
