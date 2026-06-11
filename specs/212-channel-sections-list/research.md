# Research: YT-212 Layer 2 Tool `channelSections_list`

## Decision: Treat YT-212 as a single endpoint-backed public Layer 2 tool

**Rationale**: The seed identifies YT-212 as Layer 2 Tool `channelSections_list`, mapped to `channelSections.list`, with dependencies on YT-112, YT-201, and YT-202. The PRD defines Layer 2 as raw or near-raw endpoint exposure, not a composed channel layout analysis workflow. This slice should therefore expose only the channel-section listing endpoint through MCP-facing metadata, validation, handler behavior, examples, and registration.

**Alternatives considered**:

- Build a higher-level channel layout, playlist expansion, or video enrichment tool: rejected because ranking, enrichment, playlist item expansion, video metadata expansion, and layout recommendations belong to Layer 3 or separate endpoint slices.
- Add another Layer 1 wrapper: rejected because YT-112 already provides the Layer 1 `channelSections.list` wrapper.
- Keep only representative metadata: rejected because YT-212 is an individual executable Layer 2 endpoint tool slice.

## Decision: Use official YouTube `channelSections.list` endpoint facts as the public contract baseline

**Rationale**: The official YouTube reference describes `channelSections.list` as `GET https://www.googleapis.com/youtube/v3/channelSections`, returning zero or more `channelSection` resources that match request criteria, with an official quota cost of 1 unit. The current reference identifies `part` as required and the exact-one filters as `channelId`, `id`, and `mine`. The public contract should expose those facts before invocation and preserve near-raw channel-section collection semantics.

**Alternatives considered**:

- Hide official filter and caveat details to keep the tool simpler: rejected because callers need selector, auth, and caveat visibility before invocation.
- Treat the tool as a channel layout summary tool: rejected because Layer 2 must stay close to the upstream endpoint and avoid heuristic interpretation.
- Treat a no-match lookup as an error: rejected because the endpoint returns a collection of matching resources, which can be empty for valid criteria.

## Decision: Support `channelId`, `id`, and `mine` selector modes for YT-212

**Rationale**: The official reference requires exactly one filter from `channelId`, `id`, and `mine`. YT-112's Layer 1 wrapper already models those as mutually exclusive selectors, with public API-key style behavior for `channelId` and `id`, and owner-scoped OAuth behavior for `mine`. The public tool should require exactly one supported selector and reject missing, empty, unsupported, or conflicting selector combinations before endpoint execution.

**Alternatives considered**:

- Add arbitrary channel handle or username lookup: rejected because that belongs to `channels.list`, not `channelSections.list`.
- Infer a channel from other caller context: rejected because it invents behavior beyond the endpoint.
- Silently prefer one selector when multiple are present: rejected because it changes request meaning and can mask authorization errors.

## Decision: Model auth as mixed/conditional by selector

**Rationale**: Official docs state that `mine` can only be used in a properly authorized request and returns channel sections associated with the authenticated user's YouTube channel. Public selectors such as `channelId` and `id` can use API-key style access in the existing Layer 1 wrapper. The public contract should declare `mixed/conditional` auth and make the OAuth requirement for `mine` visible in metadata, usage notes, examples, and validation errors.

**Alternatives considered**:

- Declare `api_key` for the whole tool: rejected because `mine` is owner-scoped and authorization-sensitive.
- Declare `oauth_required` for the whole tool: rejected because public selector paths are valid without owner-scoped authorization in the existing contract.
- Attempt OAuth automatically for all selectors: rejected because it obscures selector-specific access expectations and complicates direct endpoint use.

## Decision: Document official caveats for `hl` deprecation and content-owner delegation

**Rationale**: The current official reference marks `hl` as deprecated for localized metadata, noting that this behavior has been deprecated in YouTube Studio and the YouTube app. The reference also documents `onBehalfOfContentOwner` as an authorization-sensitive parameter intended exclusively for YouTube content partners. YT-212 should make both caveats visible to callers and maintainers without broadening the public tool beyond the YT-112 dependency.

**Alternatives considered**:

- Omit `hl` entirely: rejected because the official deprecation caveat is explicitly relevant to channel-section listing and the feature spec requires caveats to be clear.
- Treat `hl` as fully supported without warning: rejected because that would hide current official deprecation guidance.
- Add full content-owner partner behavior in this slice: rejected because the public Layer 2 slice should rely on the existing YT-112 wrapper contract and avoid partner-specific scope expansion unless planned as a dependency update.

## Decision: Do not promise first-class pagination request controls unless supported by the final endpoint contract

**Rationale**: The YT-212 spec requires preserving pagination details when present, and the existing YT-112 wrapper currently lists `pageToken` and `maxResults` as optional fields. The current official `channelSections.list` reference does not list `pageToken`, `maxResults`, `nextPageToken`, `prevPageToken`, or `pageInfo`. The public contract should therefore preserve continuation fields if returned by the existing dependency or upstream-compatible fixtures, but it should not claim unsupported pagination controls as a core official endpoint behavior without validation.

**Alternatives considered**:

- Promise full pagination support unconditionally: rejected because current official docs do not list pagination controls for this endpoint.
- Remove any mention of pagination from the result contract: rejected because the feature spec and existing wrapper expect preserving continuation fields when present.
- Fail any returned pagination field as unexpected: rejected because Layer 2 response shaping should preserve safe upstream fields rather than discard them.

## Decision: Preserve requested parts, channel-section items, selected lookup mode, caveat context, and safe operation context

**Rationale**: The Layer 2 response should remain near-raw enough for power users and future composition. Successful results should include endpoint identity, quota cost, returned `items`, requested parts, selected selector name, and optional continuation fields if present. A valid no-match lookup should return a successful empty item collection.

**Alternatives considered**:

- Return only a simplified channel-section summary: rejected because Layer 2 should preserve upstream resource fields rather than invent a higher-level summary.
- Expand channel sections into playlist items, videos, or channels: rejected because those are separate endpoint or Layer 3 behaviors.
- Add layout ranking or recommendations: rejected because that crosses into heuristic Layer 3 work.

## Decision: Add a channel-sections Layer 2 resource-family module and default registration

**Rationale**: Existing concrete Layer 2 tools use `YouTubeToolContract`, safe metadata validation, per-tool input schema constants, per-tool error classes, result mappers, handler builders, descriptor builders, exports, and dispatcher registration. The repo already has Layer 1 `channel_sections.py`, but no concrete Layer 2 `youtube_common/channel_sections.py` module. YT-212 should create that module and register `channelSections_list` by default so public MCP clients can discover the executable tool.

**Alternatives considered**:

- Put channel-section behavior into `channels.py`: rejected because `channelSections` is a separate YouTube resource family and YT-201 favors resource-family cohesion.
- Implement through dispatcher-only inline descriptors: rejected because it would duplicate conventions and make later channel-section slices harder to maintain.
- Create a generic list-selector framework now: rejected because one endpoint does not justify a broader abstraction unless later slices reveal real duplication.

## Decision: Use shared safe error categories with endpoint-specific guidance

**Rationale**: YT-201/YT-202 establish shared Layer 2 error categories. The official endpoint documents `channelSectionForbidden`, `idInvalid`, `invalidCriteria`, `channelNotFound`, and `channelSectionNotFound`. The tool should map validation and upstream failures into safe categories such as `invalid_request`, `authentication_failed`, `authorization_failed`, `resource_not_found`, `quota_exhausted`, `endpoint_unavailable`, and `upstream_failure`, with endpoint-specific details that do not expose secrets or private channel data.

**Alternatives considered**:

- Return raw upstream errors directly: rejected because MCP clients need stable safe error categories.
- Collapse all lookup failures into one generic failure: rejected because callers need to distinguish invalid selectors, auth failures, missing resources, quota failures, and unavailable-service cases.
- Log private channel details for debugging: rejected because public metadata, errors, and logs must not expose private channel data or credentials.

## Decision: Maintain constitution gates through TDD, full-suite validation, and docstrings

**Rationale**: The constitution requires contract-first design, Red-Green-Refactor, integration and regression coverage, full-suite validation after final code changes, and reStructuredText docstrings for every new or changed Python function. The plan therefore requires failing tests before implementation, focused checks during Green, cleanup plus `python3 -m pytest` and `python3 -m ruff check .` in Refactor, and docstrings for builders, validators, selector helpers, auth-context helpers, handlers, mappers, registration helpers, and examples.

**Alternatives considered**:

- Use only targeted tests: rejected because the constitution requires a full repository test-suite run after final code changes.
- Skip docstrings for small helpers: rejected because every new or changed Python function requires reStructuredText docstrings.
- Defer contracts until implementation: rejected because MCP-facing behavior must be contract-first.

## Sources

- Official `channelSections.list` reference: https://developers.google.com/youtube/v3/docs/channelSections/list
- Local Layer 1 dependency: `/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/`
- Local Layer 2 shared contracts: `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/`
