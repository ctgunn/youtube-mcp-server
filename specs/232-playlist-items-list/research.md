# Phase 0 Research: Layer 2 Tool `playlistItems_list`

## Decision: Implement a new Layer 2 `playlist_items` resource-family module

**Rationale**: `playlist_items` already appears in the shared resource-family registry, and the Layer 1 dependency exists under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/playlist_items.py`. Adding `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py` follows the established Layer 2 resource-family shape used by `playlist_images`, `comments`, and `comment_threads` while keeping playlist item behavior separate from playlists, playlist images, search, captions, transcripts, and higher-level workflow tools.

**Alternatives considered**:

- Add `playlistItems_list` to the existing `playlist_images.py` module. Rejected because playlist images and playlist items are different upstream resources and already have separate Layer 1 modules and resource-family registry entries.
- Add the tool directly in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`. Rejected because existing endpoint-backed YouTube tools centralize contract, schema, handler, examples, and result mapping in `youtube_common` family modules, with the dispatcher only registering descriptors.
- Delay a dedicated module until all playlist item tools are implemented. Rejected because YT-232 is independently deliverable and should create the family surface that later insert/update/delete slices can extend.

## Decision: Rely on the existing YT-132 Layer 1 `playlistItems.list` wrapper

**Rationale**: The feature specification depends on YT-132, and local Layer 1 coverage already includes `build_playlist_items_list_wrapper()` with quota cost `1`, resource identity `playlistItems`, method `list`, required `part`, supported selectors `playlistId` and `id`, API-key access expectations for the supported selector set, selector validation, paging behavior, empty-result success handling, and upstream failure preservation. Layer 2 should expose that capability through public MCP metadata, validation, result shaping, examples, exports, and registration rather than redefining upstream execution.

**Alternatives considered**:

- Reimplement upstream request shaping in Layer 2. Rejected because YT-201/YT-202 Layer 2 conventions require low-level public tools to rely on Layer 1 execution instead of duplicating request execution, auth, quota, and upstream error logic.
- Modify Layer 1 as part of this slice. Rejected unless implementation tests reveal a narrow metadata or export gap, because the existing YT-132 wrapper is the declared dependency and scope boundary.

## Decision: Public input contract requires `part` plus exactly one selector

**Rationale**: The tool should preserve endpoint-like behavior while staying testable and unambiguous. The public schema will require `part`, support `playlistId` for playlist-scoped retrieval, support `id` for identifier-based retrieval, and reject requests that omit selectors or combine selectors. Part selection should be validated against the supported Layer 1 contract so unsupported or ambiguous part values fail locally with clear guidance.

**Alternatives considered**:

- Allow requests with no selector and pass them upstream. Rejected because the feature spec requires clear validation for missing selectors and the Layer 1 contract treats supported selector choice as explicit.
- Allow both `playlistId` and `id` and let upstream decide precedence. Rejected because it creates ambiguous caller intent and violates the spec's conflicting-selector behavior.
- Expand selector support beyond `playlistId` and `id`. Rejected because YT-132 and YT-232 scope the supported public selector set to these lookup modes.

## Decision: Preserve playlist-scoped pagination and reject selector-incompatible paging

**Rationale**: Playlist traversal needs page tokens and maximum result count to support multi-page playlist item retrieval. The public contract should expose `pageToken` and `maxResults` for playlist-scoped retrieval, preserve returned page context, and reject paging inputs for selector modes where the shared contract does not support paging. This avoids silently ignoring user input and keeps empty successful collections distinct from invalid requests.

**Alternatives considered**:

- Omit pagination from the Layer 2 contract. Rejected because the seed explicitly calls out pagination behavior and playlist traversal depends on it.
- Accept paging controls with every selector. Rejected because identifier-based lookup is not a traversal workflow in the supported contract, and the spec requires selector-specific paging behavior to be documented clearly.
- Ignore invalid paging controls. Rejected because silent ignored input makes caller debugging difficult and conflicts with the project's deterministic tooling principle.

## Decision: Use API-key access disclosure for the supported selector set

**Rationale**: The YT-132 Layer 1 plan and spec identify API-key access for the supported `playlistItems.list` selector set. YT-232 should carry that expectation into public Layer 2 metadata, examples, quickstart, and errors so callers can understand access requirements before invocation.

**Alternatives considered**:

- Declare OAuth-required access for all playlist item listing. Rejected because it conflicts with the local YT-132 dependency for this supported selector set.
- Declare mixed/conditional access without selector-specific detail. Rejected because it would make the contract less clear for this slice and introduce a clarification that local dependency evidence already resolves.

## Decision: Return near-raw list results with explicit context

**Rationale**: Layer 2 public endpoint tools stay close to upstream request and response semantics while making results MCP-friendly. `playlistItems_list` should return the playlist item collection, selected parts, lookup selector, paging context when applicable, quota context, access context, endpoint identity, and safe upstream fields. It must distinguish populated success from empty success and keep validation, access, quota, missing-resource, unavailable-service, deprecated-behavior, and unexpected upstream failures in the shared safe error model.

**Alternatives considered**:

- Normalize playlist items into higher-level video summaries. Rejected because that belongs to Layer 3 tools such as playlist and channel video workflows.
- Fetch video, playlist, channel, or transcript details for returned items. Rejected because the feature must remain a single endpoint-backed Layer 2 tool.
- Treat empty results as an error. Rejected because empty playlist item collections are a valid list outcome and the spec requires a successful empty collection path.

## Decision: Register `playlistItems_list` by default and export public symbols

**Rationale**: Existing Layer 2 tools are discoverable through the default dispatcher and exported from `mcp_server.tools.youtube_common`. YT-232 should add `build_playlist_items_list_tool_descriptor()` to the default registry, export `PLAYLIST_ITEMS_LIST_*` symbols, and include contract/catalog tests so `server_list_tools` exposes the public metadata consistently.

**Alternatives considered**:

- Leave the descriptor unregistered until later playlist item tools are complete. Rejected because YT-232 is independently valuable and the feature spec requires public exposure.
- Register via ad hoc dispatcher code only. Rejected because endpoint-backed YouTube tools use resource-family descriptor builders, public exports, and shared contract metadata.

## Decision: Validate with focused contract, unit, integration, full-suite, and lint checks

**Rationale**: The constitution requires contract-first design, Red-Green-Refactor sequencing, integration coverage, and a full repository test-suite run after final changes. Focused coverage should include discovery metadata, schema, examples, validation, result mapping, safe errors, registry discovery, and dispatcher execution. Final evidence should include focused checks, `pytest`, and `ruff check .`.

**Alternatives considered**:

- Rely only on unit tests. Rejected because public MCP discovery and dispatcher registration are integration boundaries.
- Rely only on full-suite validation. Rejected because focused contract and validation tests make the endpoint behavior reviewable and protect the narrow feature scope.

## Decision: Require reStructuredText docstrings for all new or changed Python functions

**Rationale**: The constitution explicitly requires every new or modified Python function to include a reStructuredText docstring documenting purpose, inputs, outputs, raised errors when relevant, and side effects when relevant. This applies to contract builders, descriptor builders, handlers, validators, result mappers, upstream-error mappers, local transport/executor helpers, touched Layer 1 helpers, and test fake wrapper methods.

**Alternatives considered**:

- Add docstrings only to public builders. Rejected because the constitution applies to every new or modified Python function.
- Defer docstrings to implementation review. Rejected because the plan and tasks must capture docstring work up front.
