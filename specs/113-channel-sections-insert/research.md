# Research: YT-113 Layer 1 Endpoint `channelSections.insert`

## Decision: Model `channelSections.insert` as an OAuth-required write wrapper with one deterministic `part` plus `body` request shape

**Rationale**: Local product artifacts already define `channelSections.insert` as `Auth: oauth_required` with inputs of `part` plus a channel-section resource body. The official endpoint contract also requires authorization and a request body, so the smallest consistent fit is one write wrapper with required `part` and `body` fields rather than loosely shaped create inputs. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `https://developers.google.com/youtube/v3/docs/channelSections/insert`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`

**Alternatives considered**:

- Treat `channelSections.insert` as mixed or conditional auth. Rejected because neither the local inventory nor the official endpoint describes a public create path.
- Allow create inputs without a stable `body` field. Rejected because existing Layer 1 write-wrapper patterns keep request shapes deterministic and reviewable.
- Split create behavior into multiple wrapper variants by section type. Rejected because the repo pattern remains one wrapper per endpoint slice.

## Decision: Represent section-content rules as explicit contract-visible type profiles keyed by `snippet.type`

**Rationale**: The official endpoint describes section creation rules that depend on `snippet.type`, including when `contentDetails.playlists[]`, `contentDetails.channels[]`, or `snippet.title` are required, forbidden, or constrained. Keeping those rules visible in the wrapper contract lets maintainers understand supported create shapes without reading implementation code or upstream docs. Sources: `https://developers.google.com/youtube/v3/docs/channelSections`, `https://developers.google.com/youtube/v3/docs/channelSections/insert`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/spec.md`

**Alternatives considered**:

- Hide section-type rules in code only. Rejected because the feature seed explicitly requires content-structure requirements to stay visible in the wrapper contract.
- Treat all section types as sharing one generic content schema. Rejected because playlist-backed and channel-backed sections have materially different required fields.
- Limit the contract to `singlePlaylist` only. Rejected because the endpoint and product inventory imply broader section-type support.

## Decision: Validate playlist, channel, and title rules before execution

**Rationale**: The official contract states that `singlePlaylist` requires exactly one playlist, `singlePlaylist` and `multiplePlaylists` require playlist IDs, `multipleChannels` requires channel IDs, and `multiplePlaylists` and `multipleChannels` require a title. Existing `EndpointRequestShape` patterns prefer deterministic pre-execution validation, so the safest boundary is to reject malformed create bodies before they are treated as supported wrapper usage. Sources: `https://developers.google.com/youtube/v3/docs/channelSections/insert`, `https://developers.google.com/youtube/v3/docs/channelSections`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`

**Alternatives considered**:

- Forward malformed combinations upstream and rely on upstream errors. Rejected because downstream callers need stable Layer 1 boundaries.
- Silently rewrite content details to match the selected type. Rejected because hidden coercion weakens the contract and complicates debugging.
- Accept duplicate channels or playlists for forward compatibility. Rejected because the official endpoint explicitly rejects duplicated entries.

## Decision: Keep optional delegation inputs explicit but limited to the officially documented owner-partner fields

**Rationale**: The official endpoint documents `onBehalfOfContentOwner` and `onBehalfOfContentOwnerChannel` as optional authorized request parameters for content partners. Keeping those fields reviewable but optional allows the wrapper contract to describe partner-specific delegation without broadening the slice into a separate partner workflow. Sources: `https://developers.google.com/youtube/v3/docs/channelSections/insert`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/spec.md`

**Alternatives considered**:

- Omit delegation guidance entirely. Rejected because it is part of the official create contract and can materially affect higher-layer reuse.
- Treat partner delegation as mandatory. Rejected because most authorized requests should not require partner context.
- Introduce a separate wrapper for delegated creation. Rejected because one endpoint slice does not justify a second abstraction.

## Decision: Preserve distinct failure boundaries for authorization, invalid create shape, and upstream create-limit or resource-validation failures

**Rationale**: YT-113 requires downstream callers to distinguish missing authorization from malformed section definitions. The official endpoint also documents create-specific upstream failures such as maximum section count, duplicated playlists or channels, inactive channels, and unsupported section creation. Keeping auth and local validation separate from normalized upstream failures preserves higher-layer recovery choices. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/spec.md`, `https://developers.google.com/youtube/v3/docs/channelSections/insert`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/111-channels-update-wrapper/research.md`

**Alternatives considered**:

- Flatten all failures into one invalid category. Rejected because caller remediation differs between auth problems, malformed requests, and upstream refusal.
- Treat create-limit failures as local validation errors. Rejected because those limits depend on upstream channel state.
- Over-specialize failure categories beyond the slice needs. Rejected because the smallest useful split is auth vs invalid create shape vs normalized upstream failure.

## Decision: Keep the implementation seam centered on the existing integration wrapper, executor, and transport modules with focused channel-sections contract coverage

**Rationale**: Recent endpoint slices show a stable extension path through `wrappers.py`, `youtube.py`, and the Layer 1 unit, transport, integration, and contract tests. Reusing that seam is the smallest and safest approach for a single create wrapper. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`

**Alternatives considered**:

- Add a new dedicated `channel_sections.py` integration module immediately. Rejected because one endpoint slice does not justify new architecture.
- Limit validation to unit tests only. Rejected because the constitution requires integration and regression coverage.
- Put all endpoint-specific assertions into generic metadata tests only. Rejected because section-type rules and create-write boundaries need focused contract coverage.

## Clarification Closure

All planning-time clarifications for YT-113 are resolved in this research artifact. No `NEEDS CLARIFICATION` markers remain.
