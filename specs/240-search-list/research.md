# Research: YT-240 Layer 2 Tool `search_list`

## Decision: Add a concrete Layer 2 search resource-family module

**Rationale**: The seed slice requires public Layer 2 exposure of `search.list`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py` already reserves the `search` resource family with expected module and test locations. The current shared examples include only a representative `search_list` placeholder, while no concrete `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py` module exists. The narrowest cohesive implementation is to add that module with constants, validation, list result mapping, contract metadata, examples, descriptor, handler, exports, and registry integration.

**Alternatives considered**:
- Add `search_list` to `videos.py`, `channels.py`, or `playlists.py`. Rejected because search is its own upstream resource family and would blur endpoint ownership.
- Keep only the existing representative catalog entry. Rejected because YT-240 requires a public endpoint-backed Layer 2 tool, not a representative example.
- Create a higher-level research search tool. Rejected because Layer 3 and retrieval tools own enrichment, ranking, and research-ready workflows.

## Decision: Reuse the existing Layer 1 `build_search_list_wrapper()`

**Rationale**: The local Layer 1 wrapper in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/search.py` already models `search.list` with resource `search`, method `list`, path `/youtube/v3/search`, quota cost `100`, conditional auth, required `part` plus `q`, supported refinements, pagination inputs, and a quota caveat. Reusing it keeps upstream request execution, auth validation, quota metadata, and response normalization in the Layer 1 dependency rather than redefining a parallel upstream contract.

**Alternatives considered**:
- Duplicate request execution or upstream shaping in Layer 2. Rejected because Layer 2 should depend on Layer 1 wrappers and avoid duplicating execution, auth, quota, and upstream error behavior.
- Expand the Layer 1 wrapper during this slice. Rejected unless tests expose a missing export or metadata defect, because the YT-240 scope is the public Layer 2 tool.

## Decision: Require `part` and `q` for supported baseline search requests

**Rationale**: The YT-140 wrapper declares `part` and `q` as required fields. The public Layer 2 contract should preserve that boundary for deterministic baseline search behavior while documenting supported optional refinements such as `type`, `channelId`, `publishedAfter`, `publishedBefore`, `regionCode`, `relevanceLanguage`, `safeSearch`, `order`, `pageToken`, and `maxResults`.

**Alternatives considered**:
- Allow selector-only searches without `q`. Rejected because the local Layer 1 wrapper requires `q` and YT-240 should not broaden the upstream contract.
- Accept arbitrary YouTube search parameters. Rejected because the public tool should expose the supported contract and reject undocumented modifiers.
- Add a query-building convenience layer. Rejected because that belongs to higher-level Layer 3 workflows, not direct endpoint exposure.

## Decision: Model auth as conditional API-key or OAuth-backed access

**Rationale**: The Layer 1 wrapper uses API-key auth for baseline public search requests and requires OAuth-backed access when restricted filters are present. The restricted filters are `forContentOwner`, `forDeveloper`, and `forMine`; they are mutually exclusive. The Layer 2 contract must disclose this before invocation so callers can distinguish public search, restricted search, missing authorization, and empty public results.

**Alternatives considered**:
- Declare all searches API-key only. Rejected because restricted filters require stronger authorization.
- Declare all searches OAuth-required. Rejected because baseline public search can use API-key auth and that would misrepresent the public path.
- Hide auth selection behind a generic access field. Rejected because callers need to understand quota and access impact before spending 100 quota units.

## Decision: Preserve filter compatibility from the Layer 1 wrapper

**Rationale**: The Layer 1 validator already rejects multiple restricted filters and video-specific refinements unless `type=video`. Layer 2 should surface those constraints in metadata, examples, validation, and errors so callers do not spend quota on unsupported combinations. Public contract examples should cover keyword search, type-filtered search, channel-scoped search, date filtering, language or region refinement, restricted search, pagination, and invalid combinations.

**Alternatives considered**:
- Let all incompatible filters reach upstream validation. Rejected because the tool can identify known unsupported shapes locally and give clearer caller-facing feedback.
- Add deep validation for every official YouTube parameter. Rejected because the slice should remain aligned to the existing Layer 1 supported contract and avoid a broader endpoint inventory rewrite.

## Decision: Return a near-raw list result with safe query, filter, auth, quota, and paging context

**Rationale**: Search returns references and search result fields, not hydrated video, channel, playlist, transcript, analytics, ranking, recommendation, or summary records. The Layer 2 result should preserve returned upstream fields and add MCP-usable context such as endpoint identity, quota cost, submitted query, selected filters, auth path, empty-result marker, and pagination tokens when present.

**Alternatives considered**:
- Return only raw upstream output. Rejected because shared Layer 2 conventions require quota, auth, response, and error context for clients.
- Hydrate each search result through videos, channels, playlists, or transcripts. Rejected because it would add extra endpoint calls, quota consumption, and higher-level workflow behavior outside YT-240.
- Rank or summarize search results. Rejected because ranking and summarization belong to Layer 3 or retrieval workflows.

## Decision: Replace or supersede the representative catalog entry when concrete search support is added

**Rationale**: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py` currently includes a representative `_contract` for `search.list`. Once YT-240 adds a concrete `build_search_list_contract()`, the catalog should represent the real endpoint-backed tool and avoid duplicate or inconsistent metadata for the same public tool name.

**Alternatives considered**:
- Leave the placeholder alongside the concrete contract. Rejected because duplicate `search_list` entries can confuse catalog and discovery checks.
- Remove all shared catalog coverage for search. Rejected because the shared catalog uses representative examples to prove Layer 2 coverage across resource families.

## Decision: Follow existing Layer 2 list test/export patterns

**Rationale**: Existing Layer 2 list modules expose constants, input schemas, usage notes, caveats, examples, contract builders, handlers, descriptors, validators, result mappers, safe tool errors, public package exports, shared catalog entries, and default registry descriptors. YT-240 should add the same surfaces for `search_list` with focused contract, unit, integration, catalog, dispatcher, and scaffold coverage.

**Alternatives considered**:
- Add only integration tests. Rejected by the constitution and existing project practice because public tool contracts need unit, contract, and integration coverage.
- Add broad cross-resource refactors before implementing the tool. Rejected because this slice can be delivered by narrow additions to a new search family module plus exports and registration.

## Decision: Require reStructuredText docstrings for any new or changed Python functions

**Rationale**: The constitution requires every new or modified Python function to include a reStructuredText docstring documenting purpose, inputs, outputs, raised errors when relevant, and side effects when relevant. This applies to production helpers and test fake methods touched during implementation.

**Alternatives considered**:
- Rely on module-level documentation only. Rejected because the constitution specifically requires function-level docstrings for changed Python functions.
- Defer docstrings to cleanup without test or review evidence. Rejected because docstring compliance is a planning and review gate.

## Clarification Closure

All planning-time clarifications for YT-240 are resolved in this research artifact. No unresolved clarification markers remain.
