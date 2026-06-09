# Research: YT-210 Layer 2 Tool `channels_list`

## Decision: Treat YT-210 as a single endpoint-backed public Layer 2 tool

**Rationale**: The seed identifies YT-210 as Layer 2 Tool `channels_list`, mapped to `channels.list`, with dependencies on YT-110, YT-201, and YT-202. The PRD defines Layer 2 as raw or near-raw endpoint exposure, not a composed channel analytics or discovery workflow. This slice should therefore expose only the channel listing endpoint through MCP-facing metadata, validation, handler behavior, examples, and registration.

**Alternatives considered**:

- Build a higher-level channel discovery or analytics tool: rejected because ranking, enrichment, analytics, and search-style workflows belong to Layer 3 or other endpoint slices.
- Add another Layer 1 wrapper: rejected because YT-110 already provides the Layer 1 `channels.list` wrapper.
- Keep only representative metadata: rejected because YT-210 is an individual executable Layer 2 endpoint tool slice.

## Decision: Use official YouTube `channels.list` endpoint facts as the public contract baseline

**Rationale**: The official YouTube reference describes `channels.list` as `GET https://www.googleapis.com/youtube/v3/channels`, returning zero or more channel resources, with an official quota cost of 1 unit. The official docs identify `part` as required and document selector filters including `id`, `mine`, `forHandle`, `forUsername`, `managedByMe`, and deprecated `categoryId`, with an error when more than one filter is specified. YT-210's public contract should expose the slice-supported selectors before invocation and preserve near-raw channel collection semantics.

**Alternatives considered**:

- Hide official selector caveats to keep the tool simpler: rejected because callers need selector and auth visibility before invocation.
- Treat the tool as search-like by accepting arbitrary text queries: rejected because `search.list` is a separate endpoint and this tool must stay close to `channels.list`.
- Treat a no-match lookup as an error: rejected because the official endpoint returns a collection of zero or more resources.

## Decision: Support `id`, `mine`, `forHandle`, and `forUsername` selector modes for YT-210

**Rationale**: The YT-210 feature spec requires `id`, `mine`, `forHandle`, and username-style lookup. Official docs name username-style lookup as `forUsername`, and the YT-110 Layer 1 wrapper already models `id`, `mine`, `forHandle`, and `forUsername` as mutually exclusive selectors. The public tool should require exactly one of these selectors and reject missing, empty, unsupported, or conflicting selector combinations.

**Alternatives considered**:

- Expose `managedByMe` in the first public tool contract: rejected for this slice because the seed and spec call out the four required selectors, while content-owner managed-channel listing adds partner-only constraints that can be planned separately if needed.
- Use a generic `username` field instead of `forUsername`: rejected because Layer 2 should preserve upstream naming where practical.
- Silently prefer one selector when multiple are present: rejected because it changes request meaning and can mask authorization errors.

## Decision: Model auth as mixed/conditional by selector

**Rationale**: Official docs state that `mine` can only be used in a properly authorized request and returns channels owned by the authenticated user. Public selectors such as `id`, `forHandle`, and `forUsername` can use public API-key style access in the existing Layer 1 wrapper. The public contract should declare `mixed/conditional` auth and make the OAuth requirement for `mine` visible in metadata, usage notes, examples, and validation errors.

**Alternatives considered**:

- Declare `api_key` for the whole tool: rejected because `mine` is owner-scoped and authorization-sensitive.
- Declare `oauth_required` for the whole tool: rejected because public selector paths are valid without owner-scoped authorization in the existing contract.
- Attempt OAuth automatically for all selectors: rejected because it obscures selector-specific access expectations and complicates direct endpoint use.

## Decision: Preserve requested parts, channel items, pagination, selected lookup mode, and empty collections

**Rationale**: The Layer 2 response should remain near-raw enough for power users and future composition. Successful results should include endpoint identity, quota cost, returned `items`, requested parts, selected selector name, and pagination fields such as `nextPageToken`, `prevPageToken`, and `pageInfo` when present. A valid no-match lookup should return a successful empty item collection.

**Alternatives considered**:

- Return only a simplified channel summary: rejected because Layer 2 should preserve upstream resource fields rather than invent a higher-level summary.
- Drop pagination tokens from results: rejected because callers need continuation support for endpoint parity.
- Add channel video or playlist expansion: rejected because those are separate endpoint or Layer 3 behaviors.

## Decision: Reuse the existing Layer 2 contract primitives and add a channels resource-family module

**Rationale**: Existing concrete Layer 2 tools use `YouTubeToolContract`, `ResponseBoundary`, safe metadata validation, per-tool input schema constants, per-tool error classes, result mappers, handler builders, descriptor builders, exports, and dispatcher registration. The repo does not yet have `src/mcp_server/tools/youtube_common/channels.py`, so YT-210 should create that module and export it through `youtube_common/__init__.py`.

**Alternatives considered**:

- Put channel behavior into `activities.py` or `channel_banners.py`: rejected because resource-family cohesion is required by YT-201.
- Implement through dispatcher-only inline descriptors: rejected because it would duplicate conventions and make future channel slices harder to maintain.
- Create a generic selector-list module now: rejected because one endpoint does not justify a broader abstraction unless later slices reveal real duplication.

## Decision: Register `channels_list` by default in the public tool catalog

**Rationale**: Prior Layer 2 endpoint slices register executable tools in `InMemoryToolDispatcher._baseline_tool_definitions()` so clients can discover them through normal tool listing. YT-210 should add `build_channels_list_tool_descriptor()` to the default registry while preserving existing baseline, retrieval, activities, captions, and channel banner tools.

**Alternatives considered**:

- Require manual registration by callers: rejected because the public v1 Layer 2 tool catalog should be discoverable by default.
- Register as representative-only metadata: rejected because this slice is for an executable public endpoint tool.

## Decision: Use shared safe error categories with endpoint-specific guidance

**Rationale**: YT-201/YT-202 establish shared Layer 2 error categories. The official endpoint documents `invalidCriteria` when too many filters are specified, `channelForbidden` for unsupported or unauthorized requests, and `channelNotFound` for missing channel IDs. The tool should map validation and upstream failures into safe categories such as `invalid_request`, `authentication_failed`, `authorization_failed`, `resource_not_found`, `quota_exhausted`, `endpoint_unavailable`, and `upstream_failure`, with endpoint-specific details that do not expose secrets or private channel data.

**Alternatives considered**:

- Return raw upstream errors directly: rejected because MCP clients need stable safe error categories.
- Collapse all lookup failures into one generic failure: rejected because callers need to distinguish invalid selectors, auth failures, missing resources, quota failures, and unavailable-service cases.

## Decision: Maintain constitution gates through TDD, full-suite validation, and docstrings

**Rationale**: The constitution requires contract-first design, Red-Green-Refactor, integration and regression coverage, full-suite validation after final code changes, and reStructuredText docstrings for every new or changed Python function. The plan therefore requires failing tests before implementation, focused checks during Green, cleanup plus `python3 -m pytest` and `python3 -m ruff check .` in Refactor, and docstrings for builders, validators, selector helpers, auth-context helpers, handlers, mappers, registration helpers, and examples.

**Alternatives considered**:

- Use only targeted tests: rejected because the constitution requires a full repository test-suite run after final code changes.
- Skip docstrings for small helpers: rejected because every new or changed Python function requires reStructuredText docstrings.
- Defer contracts until implementation: rejected because MCP-facing behavior must be contract-first.

## Sources

- Official `channels.list` reference: https://developers.google.com/youtube/v3/docs/channels/list
- Official channel implementation guide: https://developers.google.com/youtube/v3/guides/implementation/channels
- Local Layer 1 dependency: `/Users/ctgunn/Projects/youtube-mcp-server/specs/110-channels-list-wrapper/`
- Local Layer 2 shared contracts: `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/`
