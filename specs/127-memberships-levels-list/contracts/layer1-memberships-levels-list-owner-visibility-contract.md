# Contract: YT-127 Layer 1 `membershipsLevels.list` Owner Visibility Contract

## Purpose

Define how maintainers and future higher-layer authors should interpret `membershipsLevels.list` authorization requirements, owner-only visibility expectations, unsupported modifiers, and success-versus-failure boundaries when reusing the internal Layer 1 wrapper.

The representative implementation for this contract remains under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Authorization Expectations

- `membershipsLevels.list` requires OAuth-required access
- `membershipsLevels.list` is limited to owner-only visibility
- public API-key-only membership-level retrieval is not part of the supported contract for this slice
- owner-scoped eligibility must remain visible in maintainer-facing notes and tests
- missing or ineligible owner authorization must fail distinctly from malformed membership-level requests

The contract must let maintainers tell, before implementation review, that membership-level retrieval is owner-scoped and not interchangeable with public API-key list endpoints.

## Supported Membership-Level Boundary

The owner-visibility contract must make these retrieval expectations reviewable:

- the request must include required `part`
- unsupported top-level inputs must fail clearly rather than being ignored silently
- filters, paging inputs, and delegation-related inputs are unsupported in this slice because the current repo-local contract does not name stable supported fields beyond `part`
- the feature does not broaden scope into public MCP tooling, bulk memberships administration, or generalized channel-management workflows

## Failure Boundary Expectations

Higher layers must be able to distinguish:

- auth failures caused by missing or incompatible OAuth access
- visibility failures caused by lacking the owner-only access needed to retrieve membership-level data
- local validation failures caused by incomplete or malformed membership-level requests
- successful empty membership-level results caused by valid owner-authorized requests with no returned records
- normalized upstream membership-level failures that survive local validation

The contract must make it clear that unsupported request boundaries are enforced locally before a request is treated as supported wrapper usage.

## Review Validation Expectations

The feature must prove that maintainers can identify:

- that `membershipsLevels.list` requires OAuth-required access
- that membership-level retrieval is owner-only
- that required `part` defines the supported request boundary
- that filters, paging inputs, and delegation-related inputs are unsupported in this slice
- that malformed requests fail differently from access problems
- that valid owner-authorized empty results remain distinct from validation and access failures

Validation must include:

- unit coverage for auth and request-shape validation boundaries
- contract coverage proving review surfaces expose quota, auth, owner-only visibility, and unsupported modifier guidance
- integration coverage showing compatible behavior through the existing executor flow
- transport coverage showing `GET` request construction for `membershipsLevels.list`

## Invariants

- YT-127 remains internal-only Layer 1 work
- The feature preserves existing Layer 1 metadata, executor, and higher-layer summary abstractions
- Credential material must never appear in docs, tests, or logs
- New or changed Python functions in scope include reStructuredText docstrings
