# Research: YT-209 Layer 2 Tool `channelBanners_insert`

## Decision: Treat YT-209 as a single endpoint-backed public Layer 2 tool

**Rationale**: The seed identifies YT-209 as Layer 2 Tool `channelBanners_insert`, mapped to `channelBanners.insert`, with dependencies on YT-109, YT-201, and YT-202. The PRD defines Layer 2 as raw or near-raw endpoint exposure, not a composed branding workflow. This slice should therefore expose only the banner upload endpoint through MCP-facing metadata, validation, handler behavior, examples, and registration.

**Alternatives considered**:

- Build a higher-level channel-branding update tool: rejected because activating the uploaded banner through `channels.update` is a separate endpoint and would cross into composition.
- Add another Layer 1 wrapper: rejected because YT-109 already provides the Layer 1 `channelBanners.insert` wrapper.
- Keep only representative metadata: rejected because YT-209 is an individual executable Layer 2 endpoint tool slice.

## Decision: Use official YouTube `channelBanners.insert` endpoint facts as the public contract baseline

**Rationale**: The official YouTube reference describes `channelBanners.insert` as the first upload step in a multi-step banner update flow. It uses `POST https://www.googleapis.com/upload/youtube/v3/channelBanners/insert`, supports media upload, costs 50 quota units, requires OAuth, accepts optional `onBehalfOfContentOwner`, says not to provide a request body, and returns a `channelBanner` resource when successful. The contract should expose these facts before invocation.

**Alternatives considered**:

- Hide the follow-on `channels.update` boundary to keep the tool simpler: rejected because callers could assume the uploaded image is already active.
- Present banner upload as API-key-compatible: rejected because the official method requires OAuth scopes.
- Treat the request body as a normal metadata object: rejected because the official method says not to provide a request body apart from media upload.

## Decision: Model media input as required, safe, and constrained

**Rationale**: Official documentation requires binary image data and documents a 16:9 image, minimum 2048x1152 dimensions, recommended 2560x1440 dimensions, maximum 6 MB file size, and accepted MIME types `image/jpeg`, `image/png`, and `application/octet-stream`. Local YT-109 validation already requires a media payload with `mimeType` and `content`, enforces accepted MIME types, and enforces the 6 MB limit. The public tool should require a safe media descriptor while avoiding raw image payload leakage in public examples, metadata, logs, and errors.

**Alternatives considered**:

- Accept metadata-only upload requests: rejected because the upstream method returns `mediaBodyRequired` when media is missing.
- Add local image resizing or dimension correction: rejected because image transformation is outside this endpoint-backed Layer 2 scope.
- Expose binary payloads in examples: rejected for security, privacy, and documentation safety.

## Decision: Preserve returned `channelBanner` fields and expose the URL boundary

**Rationale**: The successful upstream response returns a `channelBanner` resource. The resource URL is needed by a later `channels.update` call to set `brandingSettings.image.bannerExternalUrl`. `channelBanners_insert` should preserve returned upstream fields such as `kind`, `etag`, and `url` where present and may include safe wrapper context such as endpoint identity, quota cost, media summary, and delegation context. It must not fabricate active channel branding state.

**Alternatives considered**:

- Return only an acknowledgment: rejected because the upstream method returns a resource whose URL is essential to the caller.
- Automatically call `channels.update`: rejected because that is a separate endpoint and would create cross-endpoint composition.
- Store the returned URL for later use: rejected because this slice introduces no persistence.

## Decision: Reuse the existing Layer 2 contract primitives and add a resource-family module

**Rationale**: Existing concrete Layer 2 tools use `YouTubeToolContract`, `ResponseBoundary`, safe metadata validation, per-tool input schema constants, per-tool error classes, result mappers, handler builders, descriptor builders, and dispatcher registration. The repo does not yet have `src/mcp_server/tools/youtube_common/channel_banners.py`, so YT-209 should create that module and export it through `youtube_common/__init__.py`.

**Alternatives considered**:

- Put channel banner behavior into `captions.py`: rejected because resource-family cohesion is required by YT-201.
- Implement through dispatcher-only inline descriptors: rejected because it would duplicate conventions and make future channel banner slices harder to maintain.
- Create a generic media-upload module now: rejected because one endpoint does not justify a broader abstraction unless later slices reveal real duplication.

## Decision: Register `channelBanners_insert` by default in the public tool catalog

**Rationale**: Prior Layer 2 endpoint slices register executable tools in `InMemoryToolDispatcher._baseline_tool_definitions()` so clients can discover them through normal tool listing. YT-209 should add `build_channel_banners_insert_tool_descriptor()` to the default registry while preserving existing baseline, retrieval, activities, and captions tools.

**Alternatives considered**:

- Require manual registration by callers: rejected because the public v1 Layer 2 tool catalog should be discoverable by default.
- Register as representative-only metadata: rejected because this slice is for an executable public endpoint tool.

## Decision: Use shared safe error categories with endpoint-specific guidance

**Rationale**: YT-201/YT-202 establish shared Layer 2 error categories. The official endpoint documents `mediaBodyRequired` for missing image content and `bannerAlbumFull` when the YouTube Channel Art album has too many images. The tool should map validation and upstream failures into safe categories such as `invalid_request`, `authentication_failed`, `authorization_failed`, `quota_exhausted`, `endpoint_unavailable`, and `upstream_failure`, with endpoint-specific details that do not expose secrets or raw media.

**Alternatives considered**:

- Return raw upstream errors directly: rejected because MCP clients need stable safe error categories.
- Collapse all upload failures into one generic failure: rejected because callers need to distinguish missing media, invalid media, album-capacity, auth, quota, and unavailable-service cases.

## Decision: Maintain constitution gates through TDD, full-suite validation, and docstrings

**Rationale**: The constitution requires contract-first design, Red-Green-Refactor, integration and regression coverage, full-suite validation after final code changes, and reStructuredText docstrings for every new or changed Python function. The plan therefore requires failing tests before implementation, focused checks during Green, cleanup plus `python3 -m pytest` and `python3 -m ruff check .` in Refactor, and docstrings for builders, validators, handlers, mappers, registration helpers, and examples.

**Alternatives considered**:

- Use only targeted tests: rejected because the constitution requires a full repository test-suite run after final code changes.
- Skip docstrings for small helpers: rejected because every new or changed Python function requires reStructuredText docstrings.
- Defer contracts until implementation: rejected because MCP-facing behavior must be contract-first.
