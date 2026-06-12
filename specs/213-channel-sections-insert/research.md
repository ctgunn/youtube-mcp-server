# Research: YT-213 Layer 2 Tool `channelSections_insert`

## Decision: Treat YT-213 as a single endpoint-backed public Layer 2 tool

**Rationale**: The seed identifies YT-213 as Layer 2 Tool `channelSections_insert`, mapped to `channelSections.insert`, with dependencies on YT-113, YT-201, and YT-202. The PRD defines Layer 2 as raw or near-raw endpoint exposure, not a composed channel layout designer. This slice should therefore expose only the channel-section creation endpoint through MCP-facing metadata, validation, handler behavior, examples, and registration.

**Alternatives considered**:

- Build a higher-level channel layout automation or recommendation tool: rejected because ordering, ranking, recommendation, enrichment, and bulk layout editing belong to Layer 3 or separate endpoint slices.
- Add another Layer 1 wrapper: rejected because YT-113 already provides the Layer 1 `channelSections.insert` wrapper.
- Keep only representative metadata: rejected because YT-213 is an individual executable Layer 2 endpoint tool slice.

## Decision: Use official YouTube `channelSections.insert` endpoint facts as the public contract baseline

**Rationale**: The official YouTube reference describes `channelSections.insert` as `POST https://www.googleapis.com/youtube/v3/channelSections`, adding a channel section to the authenticated user's channel, with a maximum of 10 shelves and an official quota cost of 50 units. The current reference identifies `part` as required, lists valid parts as `contentDetails`, `id`, and `snippet`, requires authorization, and returns a `channelSection` resource when successful. The public contract should expose those facts before invocation and preserve near-raw created-resource semantics.

**Alternatives considered**:

- Hide official body and limit details to keep the tool smaller: rejected because callers need quota, OAuth, part, body, content-rule, and capacity visibility before making a write.
- Treat the tool as a channel layout summary tool: rejected because Layer 2 must stay close to the upstream endpoint and avoid heuristic interpretation.
- Return only a mutation acknowledgement: rejected because the endpoint returns the created `channelSection` resource and Layer 2 should preserve safe returned fields.

## Decision: Require OAuth for every `channelSections_insert` invocation

**Rationale**: The official endpoint requires authorization and lists YouTube OAuth scopes. The existing YT-113 Layer 1 wrapper declares `AuthMode.OAUTH_REQUIRED` and rejects non-OAuth access. The public tool should declare `oauth_required`, preflight missing OAuth before write attempts, and never present channel-section creation as API-key-only behavior.

**Alternatives considered**:

- Declare mixed auth: rejected because inserts are owner-scoped writes and do not have a public API-key path.
- Attempt unauthenticated or API-key fallback for simple sections: rejected because it would contradict the endpoint access model and risk confusing callers.
- Defer all auth failures to upstream: rejected because preflight guidance gives callers safer, clearer correction feedback before a write attempt.

## Decision: Require `part` and a channel-section `body` with `body.snippet.type`

**Rationale**: The official reference says `part` identifies properties being set and returned, and the request body must include a channel-section resource with `snippet.type`. The public input contract should require both `part` and `body`, validate that `body` is an object, and reject missing `body.snippet.type` with an endpoint-specific invalid request message.

**Alternatives considered**:

- Infer a section type from supplied playlists or channels: rejected because inference changes request meaning and hides required upstream fields.
- Make `body` optional for default shelves such as popular uploads: rejected because the upstream endpoint requires a resource body and at least `snippet.type`.
- Accept unknown part names and let upstream decide: rejected for the public contract because current official allowed insert parts are known and caller-facing validation can avoid avoidable quota-bearing failures.

## Decision: Model content-structure rules around section type and `contentDetails`

**Rationale**: The official errors show section-type-specific rules: `multipleChannels` requires channel references; `singlePlaylist` requires exactly one playlist; `singlePlaylist` and `multiplePlaylists` require playlists; channels or playlists are invalid when not expected; duplicate references and private/missing/unavailable references must surface clearly. The public tool should validate obvious structural mismatches locally where practical and map upstream resource-state failures safely.

**Alternatives considered**:

- Accept any body and rely only on upstream errors: rejected because the spec requires content-structure requirements to be documented clearly and caller-visible validation protects against predictable invalid writes.
- Fully validate all YouTube resource existence locally before insertion: rejected because that would require extra endpoint calls, extra quota, broader scope, and possible privacy exposure.
- Create or repair missing playlists/channels automatically: rejected because those are separate endpoints or higher-level workflows.

## Decision: Support partner/delegated-channel context only as documented optional write context

**Rationale**: The official endpoint documents `onBehalfOfContentOwner` and `onBehalfOfContentOwnerChannel` as partner-only parameters requiring proper authorization; the channel parameter is required when an owner value is supplied and can only be used with it. The public tool should expose those fields as optional partner context, validate paired usage, and make the partner-only authorization caveat visible before invocation.

**Alternatives considered**:

- Omit partner parameters entirely: rejected because they are part of the upstream endpoint and the spec requires OAuth and content-structure requirements to be clear.
- Treat partner parameters as ordinary public fields: rejected because they are partner-scoped and authorization-sensitive.
- Add a separate partner-only public tool: rejected because this slice maps one upstream endpoint to one public Layer 2 tool.

## Decision: Preserve created channel-section fields and safe operation context

**Rationale**: The Layer 2 response should remain near-raw enough for power users and future composition. Successful results should include endpoint identity, quota cost, returned channel-section resource fields, requested parts, safe partner-context flags when present, and safe operation context. Optional fields absent from the upstream response should not be fabricated.

**Alternatives considered**:

- Return only `created: true`: rejected because it discards the created resource returned by the endpoint.
- Expand returned playlists or channels into full metadata: rejected because those are separate endpoint or Layer 3 behaviors.
- Add layout ranking or recommendations: rejected because that crosses into heuristic Layer 3 work.

## Decision: Add insert behavior to the existing channel-sections Layer 2 module and default registration

**Rationale**: YT-212 created `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py` for the resource family. Adding `channelSections_insert` beside `channelSections_list` keeps resource-family cohesion, reuses existing shared contract primitives, and limits default registration changes to another additive descriptor.

**Alternatives considered**:

- Put insert behavior into `channels.py`: rejected because `channelSections` is a separate YouTube resource family.
- Implement through dispatcher-only inline descriptors: rejected because it would duplicate conventions and make later channel-section update/delete slices harder to maintain.
- Create a generic mutation framework now: rejected because one insert endpoint does not justify broad abstraction unless later slices reveal real duplication.

## Decision: Use shared safe error categories with endpoint-specific guidance

**Rationale**: YT-201/YT-202 establish shared Layer 2 error categories. The official endpoint documents failures for missing type, missing snippet, not editable sections, forbidden auth, inactive/missing channels, duplicate channels/playlists, missing/forbidden content details, invalid position, capacity limits, too many references, own-channel references, private playlists, title problems, and missing playlists. The tool should map validation and upstream failures into safe categories such as `invalid_request`, `authentication_failed`, `authorization_failed`, `quota_exhausted`, `resource_not_found`, `endpoint_unavailable`, and `upstream_failure`, with endpoint-specific details that do not expose secrets or private channel data.

**Alternatives considered**:

- Return raw upstream errors directly: rejected because MCP clients need stable safe error categories.
- Collapse all create failures into one generic failure: rejected because callers need to distinguish invalid body structure, missing auth, forbidden channel state, missing referenced resources, quota failures, and unavailable-service cases.
- Log private channel details for debugging: rejected because public metadata, errors, and logs must not expose private channel data or credentials.

## Decision: Maintain constitution gates through TDD, full-suite validation, and docstrings

**Rationale**: The constitution requires contract-first design, Red-Green-Refactor, integration and regression coverage, full-suite validation after final code changes, and reStructuredText docstrings for every new or changed Python function. The plan therefore requires failing tests before implementation, focused checks during Green, cleanup plus `python3 -m pytest` and `python3 -m ruff check .` in Refactor, and docstrings for builders, validators, body helpers, content-rule helpers, OAuth helpers, partner-context helpers, handlers, mappers, registration helpers, and examples.

**Alternatives considered**:

- Use only targeted tests: rejected because the constitution requires a full repository test-suite run after final code changes.
- Skip docstrings for small helpers: rejected because every new or changed Python function requires reStructuredText docstrings.
- Defer contracts until implementation: rejected because MCP-facing behavior must be contract-first.

## Sources

- Official `channelSections.insert` reference: https://developers.google.com/youtube/v3/docs/channelSections/insert
- Official `channelSections` resource overview: https://developers.google.com/youtube/v3/docs/channelSections
- Local Layer 1 dependency: `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/`
- Local Layer 2 shared contracts: `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/`
