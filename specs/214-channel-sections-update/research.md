# Research: YT-214 Layer 2 Tool `channelSections_update`

## Decision: Treat YT-214 as a single endpoint-backed public Layer 2 tool

**Rationale**: The seed identifies YT-214 as Layer 2 Tool `channelSections_update`, mapped to `channelSections.update`, with dependencies on YT-114, YT-201, and YT-202. The PRD defines Layer 2 as raw or near-raw endpoint exposure, not a composed channel layout designer. This slice should therefore expose only the channel-section update endpoint through MCP-facing metadata, validation, handler behavior, examples, and registration.

**Alternatives considered**:

- Build a higher-level channel layout automation or recommendation tool: rejected because ordering, ranking, recommendation, enrichment, patching, and bulk layout editing belong to Layer 3 or separate endpoint slices.
- Add another Layer 1 wrapper: rejected because YT-114 already provides the Layer 1 `channelSections.update` wrapper.
- Keep only representative metadata: rejected because YT-214 is an individual executable Layer 2 endpoint tool slice.

## Decision: Use official YouTube `channelSections.update` endpoint facts as the public contract baseline

**Rationale**: The official YouTube reference describes `channelSections.update` as `PUT https://www.googleapis.com/youtube/v3/channelSections`, updates a channel section, has an official quota cost of 50 units, requires authorization, requires the `part` parameter, supports part values `contentDetails`, `id`, and `snippet`, and returns a `channelSection` resource when successful. The reference also states that update requests use the submitted resource to set and return properties, and that omitted existing properties are deleted. The public contract should expose those facts before invocation and preserve near-raw updated-resource semantics.

**Alternatives considered**:

- Hide official body and overwrite details to keep the tool smaller: rejected because callers need quota, OAuth, part, target identity, body, writable-field, content-rule, and overwrite visibility before making a write.
- Treat the tool as a patch operation: rejected because the official endpoint is update-oriented and warns about deleted omitted properties.
- Return only a mutation acknowledgement: rejected because the endpoint returns the updated `channelSection` resource and Layer 2 should preserve safe returned fields.

## Decision: Require OAuth for every `channelSections_update` invocation

**Rationale**: The official endpoint requires authorization and lists YouTube OAuth scopes. The existing YT-114 Layer 1 wrapper declares OAuth-required behavior and rejects non-OAuth access. The public tool should declare `oauth_required`, preflight missing OAuth before write attempts, and never present channel-section updates as API-key-only behavior.

**Alternatives considered**:

- Declare mixed auth: rejected because updates are owner-scoped writes and do not have a public API-key path.
- Attempt unauthenticated or API-key fallback for simple metadata changes: rejected because it would contradict the endpoint access model and risk confusing callers.
- Defer all auth failures to upstream: rejected because preflight guidance gives callers safer, clearer correction feedback before a write attempt.

## Decision: Require `part`, `body`, `body.id`, and `body.snippet.type`

**Rationale**: The official reference says `part` identifies properties being set and returned, the request body must provide a `channelSection` resource, `snippet.type` must be specified, and documented errors include `idRequired`, `idInvalid`, and `snippetNeeded`. The public input contract should require `part`, an object `body`, target identity in `body.id`, and a section type in `body.snippet.type`, with clear endpoint-specific invalid request messages.

**Alternatives considered**:

- Let callers pass the target section ID as a top-level `id`: rejected because the upstream update body identity is the endpoint contract and the Layer 1 wrapper already expects the body resource.
- Infer a section type from supplied playlists or channels: rejected because inference changes request meaning and hides required upstream fields.
- Accept unknown part names and let upstream decide: rejected for the public contract because current official allowed update parts are known and caller-facing validation can avoid avoidable quota-bearing failures.

## Decision: Make overwrite-sensitive update behavior visible before invocation

**Rationale**: The official documentation warns that when an update request omits a property that already has a value, the existing value is deleted. This is materially different from partial patch behavior. The Layer 2 contract should warn callers in metadata, usage notes, examples, quickstart, and validation guidance so power users do not accidentally clear existing channel-section fields.

**Alternatives considered**:

- Hide the warning in implementation comments only: rejected because the risk affects caller behavior and must be visible through discovery and contract artifacts.
- Convert requests into patch semantics by reading existing sections first: rejected because that would require extra endpoint calls, extra quota, broader scope, and a higher-level behavior not promised by Layer 2.
- Reject updates that omit optional fields: rejected because the upstream endpoint supports updates with selected writable fields, but the caller must understand replacement behavior.

## Decision: Model content-structure rules around section type and `contentDetails`

**Rationale**: The official errors show section-type-specific rules: `multipleChannels` requires channel references; `singlePlaylist` requires exactly one playlist; `singlePlaylist` and `multiplePlaylists` require playlists; channels or playlists are invalid when not expected; duplicate references, private playlists, missing playlists, missing channels, inactive channels, own-channel references, missing titles, and excessive references must surface clearly. The public tool should validate obvious structural mismatches locally where practical and map upstream resource-state failures safely.

**Alternatives considered**:

- Accept any body and rely only on upstream errors: rejected because the spec requires writable-field expectations to be documented clearly and caller-visible validation protects against predictable invalid writes.
- Fully validate all YouTube resource existence locally before update: rejected because that would require extra endpoint calls, extra quota, broader scope, and possible privacy exposure.
- Create or repair missing playlists/channels automatically: rejected because those are separate endpoints or higher-level workflows.

## Decision: Support content-owner delegation only as documented optional write context

**Rationale**: The official update endpoint documents `onBehalfOfContentOwner` as a partner-only parameter requiring proper authorization. The public tool should expose that field as optional partner context, validate safe non-empty usage, and make the partner-only authorization caveat visible before invocation. Unlike insert, the current official update reference does not list `onBehalfOfContentOwnerChannel`, so YT-214 should not advertise it as supported unless the local Layer 1 wrapper or official reference changes.

**Alternatives considered**:

- Omit partner parameters entirely: rejected because `onBehalfOfContentOwner` is part of the upstream endpoint and the spec requires OAuth and writable-field requirements to be clear.
- Treat partner parameters as ordinary public fields: rejected because they are partner-scoped and authorization-sensitive.
- Add unsupported delegated-channel parameters from neighboring insert behavior: rejected because this update slice should stay aligned with official `channelSections.update` parameters.

## Decision: Preserve updated channel-section fields and safe operation context

**Rationale**: The Layer 2 response should remain near-raw enough for power users and future composition. Successful results should include endpoint identity, quota cost, returned channel-section resource fields, requested parts, safe partner-context flags when present, `updated: true`, and safe operation context. Optional fields absent from the upstream response should not be fabricated.

**Alternatives considered**:

- Return only `updated: true`: rejected because it discards the updated resource returned by the endpoint.
- Expand returned playlists or channels into full metadata: rejected because those are separate endpoint or Layer 3 behaviors.
- Add layout ranking or recommendations: rejected because that crosses into heuristic Layer 3 work.

## Decision: Add update behavior to the existing channel-sections Layer 2 module and default registration

**Rationale**: YT-212 and YT-213 established `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py` for the resource family. Adding `channelSections_update` beside `channelSections_list` and `channelSections_insert` keeps resource-family cohesion, reuses existing shared contract primitives, and limits default registration changes to another additive descriptor. The update-result shape should borrow from the existing `channels_update` Layer 2 pattern where it already models updated-resource metadata, while channel-section body validation should borrow from the existing `channelSections_insert` helpers where content rules overlap.

**Alternatives considered**:

- Put update behavior into `channels.py`: rejected because `channelSections` is a separate YouTube resource family.
- Implement through dispatcher-only inline descriptors: rejected because it would duplicate conventions and make the channel-section delete slice harder to maintain.
- Create a generic mutation framework now: rejected because one update endpoint does not justify broad abstraction beyond small local reuse with insert helpers.

## Decision: Use shared safe error categories with endpoint-specific guidance

**Rationale**: YT-201/YT-202 establish shared Layer 2 error categories. The official endpoint documents failures for not-editable sections, missing type, improper auth, inactive/missing channels, duplicate channels/playlists, missing/forbidden content details, invalid or missing IDs, invalid position, too many references, own-channel references, private playlists, title problems, missing snippets, missing playlists, and missing target sections. The tool should map validation and upstream failures into safe categories such as `invalid_request`, `authentication_failed`, `authorization_failed`, `quota_exhausted`, `resource_not_found`, `endpoint_unavailable`, and `upstream_failure`, with endpoint-specific details that do not expose secrets or private channel data.

**Alternatives considered**:

- Return raw upstream errors directly: rejected because MCP clients need stable safe error categories.
- Collapse all update failures into one generic failure: rejected because callers need to distinguish invalid body structure, missing auth, forbidden channel state, missing target sections, missing referenced resources, quota failures, and unavailable-service cases.
- Log private channel details for debugging: rejected because public metadata, errors, and logs must not expose private channel data or credentials.

## Decision: Maintain constitution gates through TDD, full-suite validation, and docstrings

**Rationale**: The constitution requires contract-first design, Red-Green-Refactor, integration and regression coverage, full-suite validation after final code changes, and reStructuredText docstrings for every new or changed Python function. The plan therefore requires failing tests before implementation, focused checks during Green, cleanup plus `python3 -m pytest` and `python3 -m ruff check .` in Refactor, and docstrings for builders, validators, body helpers, content-rule helpers, OAuth helpers, partner-context helpers, handlers, mappers, registration helpers, and examples.

**Alternatives considered**:

- Use only targeted tests: rejected because the constitution requires a full repository test-suite run after final code changes.
- Skip docstrings for small helpers: rejected because every new or changed Python function requires reStructuredText docstrings.
- Defer contracts until implementation: rejected because MCP-facing behavior must be contract-first.

## Sources

- Official `channelSections.update` reference: https://developers.google.com/youtube/v3/docs/channelSections/update
- Official `channelSections` resource overview: https://developers.google.com/youtube/v3/docs/channelSections
- Local Layer 1 dependency: `/Users/ctgunn/Projects/youtube-mcp-server/specs/114-channel-sections-update/`
- Local Layer 2 shared contracts: `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/`
