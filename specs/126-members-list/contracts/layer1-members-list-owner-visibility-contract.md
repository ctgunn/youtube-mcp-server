# Contract: YT-126 Layer 1 `members.list` Owner Visibility Contract

## Purpose

Define how maintainers and future higher-layer authors should interpret `members.list` authorization requirements, owner-only visibility expectations, supported paging behavior, unsupported delegation inputs, and success-versus-failure boundaries when reusing the internal Layer 1 wrapper.

The representative implementation for this contract remains under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Authorization Expectations

- `members.list` requires OAuth-required access
- `members.list` is limited to owner-only visibility
- public API-key-only membership retrieval is not part of the supported contract for this slice
- owner-scoped eligibility must remain visible in maintainer-facing notes and tests
- missing or ineligible owner authorization must fail distinctly from malformed membership requests

The contract must let maintainers tell, before implementation review, that membership retrieval is owner-scoped and not interchangeable with public API-key list endpoints.

## Supported Membership Boundary

The owner-visibility contract must make these retrieval expectations reviewable:

- the request must include one supported membership retrieval mode
- paging support is limited to explicitly documented `pageToken` and `maxResults`
- unsupported top-level inputs must fail clearly rather than being ignored silently
- delegation-related inputs are unsupported in this slice because the current repo-local contract does not name a stable supported delegation flag for `members.list`
- the feature does not broaden scope into public MCP tooling, bulk membership operations, or generalized memberships administration

## Failure Boundary Expectations

Higher layers must be able to distinguish:

- auth failures caused by missing or incompatible OAuth access
- visibility failures caused by lacking the owner-only access needed to retrieve membership data
- local validation failures caused by incomplete or malformed membership requests
- successful empty membership results caused by valid owner-authorized requests with no returned records
- normalized upstream membership failures that survive local validation

The contract must make it clear that unsupported membership boundaries are enforced locally before a request is treated as supported wrapper usage.

## Review Validation Expectations

The feature must prove that maintainers can identify:

- that `members.list` requires OAuth-required access
- that membership retrieval is owner-only
- that `part` and `mode` define the required request boundary
- that `pageToken` and `maxResults` are the only optional list-style modifiers in scope
- that delegation-related inputs are unsupported in this slice
- that malformed requests fail differently from access problems
- that valid owner-authorized empty results remain distinct from validation and access failures

Validation must include:

- unit coverage for auth and membership-shape validation boundaries
- contract coverage proving review surfaces expose quota, auth, owner-only visibility, and unsupported delegation guidance
- integration coverage showing compatible behavior through the existing executor flow
- transport coverage showing `GET` request construction for `members.list`

## Invariants

- YT-126 remains internal-only Layer 1 work
- The feature preserves existing Layer 1 metadata, executor, and higher-layer summary abstractions
- Credential material must never appear in docs, tests, or logs
- New or changed Python functions in scope include reStructuredText docstrings
