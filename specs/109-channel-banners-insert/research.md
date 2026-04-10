# Research: YT-109 Layer 1 Endpoint `channelBanners.insert`

## Decision: Keep the minimum request contract to media upload plus optional delegated content-owner context

**Rationale**: The official `channelBanners.insert` reference describes the method as a media-upload request with no JSON request body, plus an optional `onBehalfOfContentOwner` query parameter for content partners. The current Layer 1 pattern favors narrow request contracts enforced through `EndpointRequestShape.validate_arguments()`, so the smallest consistent wrapper contract is one required `media` upload payload plus optional delegation context rather than a broader multi-mode shape. Sources: `https://developers.google.com/youtube/v3/docs/channelBanners/insert`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`

**Alternatives considered**:

- Require a JSON `body` payload alongside the media upload. Rejected because the official endpoint says not to provide a request body.
- Allow arbitrary extra query parameters for future flexibility. Rejected because the current Layer 1 request-shape contract rejects undocumented fields by design.
- Model upload metadata as separate top-level fields instead of one `media` object. Rejected because nearby upload wrappers already use a single reviewable `media` payload.

## Decision: Model `channelBanners.insert` as `oauth_required` with optional content-owner delegation notes

**Rationale**: The official reference requires authorization with YouTube OAuth scopes and documents `onBehalfOfContentOwner` as an optional parameter available only in properly authorized content-partner requests. The repository's Layer 1 standards record one stable auth mode plus maintainer-facing notes, and the existing caption-management upload wrappers already treat delegation as optional context rather than a separate auth enum. Sources: `https://developers.google.com/youtube/v3/docs/channelBanners/insert`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/auth.py`

**Alternatives considered**:

- Mixed or conditional auth. Rejected because there is no API-key or public path for this endpoint in the official reference or local tool inventory.
- Separate delegated-banner wrapper. Rejected because the repository pattern is one wrapper per endpoint slice.
- Runtime-only delegation handling without metadata notes. Rejected because later channel-branding work needs the boundary visible before code inspection.

## Decision: Make image constraints part of the wrapper contract, not a transport-only detail

**Rationale**: The official reference specifies concrete upload constraints: 16:9 aspect ratio, minimum 2048x1152 resolution, recommended 2560x1440 resolution, maximum 6 MB file size, and accepted MIME types `image/jpeg`, `image/png`, and `application/octet-stream`. YT-109 explicitly requires media-upload requirements to be documented in the wrapper contract, so these constraints need to be visible in metadata notes, contract artifacts, and docstrings rather than hidden only in request-construction code. Sources: `https://developers.google.com/youtube/v3/docs/channelBanners/insert`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/spec.md`

**Alternatives considered**:

- Leave dimension and MIME guidance only in planning docs. Rejected because downstream reuse depends on a stable contract surface inside the feature artifacts.
- Validate only at transport time after building the request. Rejected because the Layer 1 contract should reject or clearly flag unsupported shapes before execution.
- Omit the recommended size and keep only minimum rules. Rejected because maintainers benefit from seeing both the hard floor and the recommended target when planning branding flows.

## Decision: Treat the returned banner URL as the key normalized outcome for follow-on `channels.update` work

**Rationale**: The official banner-upload flow is explicitly the first step in a three-step banner update process, and the response contains a `url` value that later `channels.update` work must set as `brandingSettings.image.bannerExternalUrl`. The wrapper result should therefore keep the returned banner URL reviewable and reusable, even though YT-109 itself does not implement `channels.update`. Sources: `https://developers.google.com/youtube/v3/docs/channelBanners/insert`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/spec.md`

**Alternatives considered**:

- Treat the upload as successful without preserving the returned URL in later review surfaces. Rejected because the URL is the essential handoff value for follow-on channel-branding work.
- Merge `channelBanners.insert` and `channels.update` into one wrapper slice. Rejected because YT-109 is scoped to a single endpoint-specific Layer 1 wrapper.
- Reduce the result contract to a generic success flag only. Rejected because it would hide the most important reusable output from the endpoint.

## Decision: Preserve explicit failure boundaries for missing authorization, invalid upload input, and target-channel restrictions

**Rationale**: The YT-109 spec requires downstream callers to distinguish authorization, asset-shape, and target-channel problems. The official reference also documents at least one explicit upload failure (`mediaBodyRequired`) and content-owner behavior that can fail when scope or linkage is wrong. The current integration layer already normalizes upstream failures, so the smallest consistent approach is to preserve separate normalized failure categories such as `auth`, `invalid_request`, and `target_channel` rather than flattening everything into one generic upload error. Sources: `https://developers.google.com/youtube/v3/docs/channelBanners/insert`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/spec.md`

**Alternatives considered**:

- Flatten all banner-upload failures into one generic invalid request. Rejected because it would hide access and channel-scope issues from downstream callers.
- Treat missing image data as a transport concern only. Rejected because the endpoint documents it as a meaningful request-boundary failure.
- Return ambiguous success with warning metadata when the URL is missing. Rejected because the wrapper result needs to make the upload outcome unambiguous.

## Decision: Make quota cost `50` visible in metadata, docstrings, and contract artifacts

**Rationale**: The YT-109 seed requires the official quota cost of `50` to appear in method metadata and method comments or docstrings. Existing endpoint slices use wrapper review surfaces, feature-local contracts, and tests to keep quota visible without relying on external docs, and `channelBanners.insert` should follow that same pattern. Sources: `https://developers.google.com/youtube/v3/docs/channelBanners/insert`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`

**Alternatives considered**:

- Keep quota visibility only in planning docs. Rejected because the seed requires metadata and docstring visibility.
- Rely on external YouTube docs for quota review. Rejected because nearby endpoint slices keep quota discoverable inside repository artifacts.

## Decision: Keep the implementation seam centered on `wrappers.py`, `youtube.py`, `consumer.py`, and the existing Layer 1 test suites

**Rationale**: `wrappers.py` already contains the endpoint-specific builder pattern used by existing caption wrappers, `youtube.py` is the transport seam that handles method-specific request construction and normalized success payloads, `consumer.py` provides the higher-layer review surface pattern for wrapper reuse, and the current unit, contract, integration, and transport tests already cover adjacent upload and result-handling behavior with minimal duplication. This is the smallest extension path for one more endpoint slice. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

**Alternatives considered**:

- Introduce a new channel-branding integration module immediately. Rejected because one endpoint slice does not justify a new abstraction boundary.
- Skip consumer-facing review coverage until `channels.update` is implemented. Rejected because the repository already uses representative consumer summaries to prove wrapper reviewability.
- Limit validation to unit tests only. Rejected because the constitution requires integration and regression coverage across contract boundaries.
