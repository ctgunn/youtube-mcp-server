# Research: YT-211 Layer 2 Tool `channels_update`

## Decision: Treat YT-211 as a single endpoint-backed public Layer 2 tool

**Rationale**: The seed identifies YT-211 as Layer 2 Tool `channels_update`, mapped to `channels.update`, with dependencies on YT-111, YT-201, and YT-202. The PRD defines Layer 2 as raw or near-raw endpoint exposure, not a composed channel-management workflow. This slice should therefore expose only the channel update endpoint through MCP-facing metadata, validation, handler behavior, examples, and registration.

**Alternatives considered**:

- Build a higher-level channel management or branding workflow: rejected because orchestration, enrichment, analytics, and multi-step branding workflows belong to Layer 3 or separate endpoint slices.
- Add another Layer 1 wrapper: rejected because YT-111 already provides the Layer 1 `channels.update` wrapper.
- Keep only representative metadata: rejected because YT-211 is an individual executable Layer 2 endpoint tool slice.

## Decision: Use official YouTube `channels.update` endpoint facts as the public contract baseline

**Rationale**: The official YouTube reference describes `channels.update` as `PUT https://www.googleapis.com/youtube/v3/channels`, requires authorization, requires `part`, returns a `channel` resource on success, and has an official quota cost of 50 units. The public contract should expose those facts before invocation and preserve near-raw updated channel semantics.

**Alternatives considered**:

- Hide official mutation caveats to keep the tool simpler: rejected because callers need cost, auth, part, overwrite, and validation visibility before mutating live channel metadata.
- Treat the tool as public API-key accessible: rejected because the official endpoint requires authorization and the YT-111 wrapper is OAuth-required.
- Return only an acknowledgment: rejected because the official endpoint returns a channel resource and Layer 2 should preserve endpoint result semantics.

## Decision: Keep the public writable surface aligned to the existing YT-111 boundary

**Rationale**: YT-111 implemented and documented the local Layer 1 boundary as OAuth-required updates through `brandingSettings` and `localizations`, with part-to-body validation and read-only field rejection. Although the current official reference also names `invideoPromotion` and includes additional resource-body notes, YT-211 depends on the existing YT-111 wrapper and should not silently expand Layer 1 behavior during public tool planning. The contract will record the official-doc caveat and keep YT-211 scoped to `brandingSettings` and `localizations` unless a later dependency update intentionally broadens YT-111.

**Alternatives considered**:

- Add `invideoPromotion` directly in Layer 2: rejected because the current Layer 1 wrapper does not expose that writable part and Layer 2 should not define a second upstream contract.
- Add all official body fields immediately: rejected because it would broaden YT-111 without a dedicated Layer 1 dependency update and increase mutation risk.
- Hide the official discrepancy: rejected because callers and maintainers need to understand why the public tool supports a narrower writable surface than the upstream reference.

## Decision: Require exactly one writable part per public `channels_update` request

**Rationale**: The official reference states that `part` identifies the properties the write operation sets and that only one supported part may be updated with a single request. Requiring exactly one supported part in Layer 2 gives callers deterministic mutation behavior and keeps examples simple. The selected `part` must align with a matching field in `body`.

**Alternatives considered**:

- Accept comma-separated multiple parts when the Layer 1 validator can parse them: rejected because the official public endpoint guidance says one part can be updated in one request.
- Infer the part from body fields: rejected because upstream `part` is required and affects write and response behavior.
- Permit unsupported parts and let upstream reject them: rejected because public Layer 2 validation should reject known unsupported write shapes before execution.

## Decision: Document content-owner delegation as an official caveat, not a YT-211 input

**Rationale**: The official `channels.update` reference documents content-owner delegation through `onBehalfOfContentOwner`, but the current YT-111 Layer 1 wrapper does not expose that optional field. YT-211 should therefore reject delegation fields in the public input contract and document the official caveat for a future dependency update rather than implying support that the current execution path does not provide.

**Alternatives considered**:

- Add `onBehalfOfContentOwner` directly in Layer 2: rejected because it would define a public request shape that the current Layer 1 dependency does not support.
- Expand the YT-111 wrapper inside this slice: rejected because the seed scope is a Layer 2 public tool and the existing dependency is already complete.
- Omit the delegation caveat entirely: rejected because callers and maintainers should understand the known official-doc difference.

## Decision: Model auth as OAuth-required with no public-only fallback

**Rationale**: The official reference requires authorization with one of the accepted YouTube scopes, and YT-111's wrapper enforces OAuth-required auth. `channels_update` should therefore expose `oauth_required` metadata, require eligible OAuth before invocation, and distinguish missing credentials or ineligible channel-management access from invalid request shape.

**Alternatives considered**:

- Declare mixed/conditional auth like `channels_list`: rejected because mutation paths are not public read paths.
- Accept an API key for validation-only dry runs: rejected because the tool is endpoint-backed and should not invent a non-upstream dry-run mode.
- Hide OAuth details in examples: rejected because mutation callers need access expectations before spending quota.

## Decision: Preserve updated channel resource content with safe operation context

**Rationale**: Successful results should include endpoint identity, quota cost, selected writable part, requested part names, and the returned updated channel resource content in a near-raw shape. The result should not fabricate channel-management state, banner-upload state, analytics, or cross-endpoint enrichment.

**Alternatives considered**:

- Return a high-level "updated" summary only: rejected because Layer 2 should preserve endpoint-backed resource fields.
- Include the full request body in public results: rejected because channel metadata may contain sensitive values and the returned endpoint resource should be the source of truth.
- Automatically call `channels_list` after update: rejected because that would cross from direct endpoint exposure into composition.

## Decision: Keep banner upload and banner activation visibly separate

**Rationale**: YT-209 `channelBanners_insert` uploads a banner image and returns a URL. `channels_update` may apply a returned URL through `brandingSettings.image.bannerExternalUrl`, but it must not upload media or imply banner upload occurred in the same tool. Keeping this boundary visible prevents callers from confusing upload and activation.

**Alternatives considered**:

- Merge banner upload and channel update into one tool: rejected because it crosses endpoint boundaries and becomes a composed workflow.
- Omit banner guidance from `channels_update`: rejected because channel banner activation is a common `brandingSettings` update and the YT-209 contract explicitly points to `channels.update`.
- Persist uploaded banner URLs for later update calls: rejected because this slice introduces no persistence.

## Decision: Reuse the existing channels Layer 2 module and default registration path

**Rationale**: YT-210 created `src/mcp_server/tools/youtube_common/channels.py` with concrete `channels_list` constants, contract builder, validation, handler, result mapping, descriptor, exports, and default dispatcher registration. YT-211 should extend the same resource-family module for cohesion and add `build_channels_update_tool_descriptor()` to the default registry without disturbing existing tools.

**Alternatives considered**:

- Create a separate `channel_updates.py` module: rejected because YT-201 requires resource-family cohesion and the channels module already exists.
- Implement through dispatcher-only inline descriptors: rejected because it would duplicate conventions and make future channels slices harder to maintain.
- Create a generic mutation framework now: rejected because one update endpoint does not justify broader abstraction until later update slices reveal real duplication.

## Decision: Use shared safe error categories with endpoint-specific mutation guidance

**Rationale**: YT-201/YT-202 establish shared Layer 2 error categories. Official `channels.update` documents invalid branding/localization values, channel title update restrictions, missing or inaccessible channels, authorization failures, and other upstream errors. The tool should map validation and upstream failures into safe categories such as `invalid_request`, `authentication_failed`, `authorization_failed`, `resource_not_found`, `quota_exhausted`, `endpoint_unavailable`, and `upstream_failure`, with endpoint-specific details that do not expose secrets or private channel data.

**Alternatives considered**:

- Return raw upstream errors directly: rejected because MCP clients need stable safe error categories.
- Collapse all mutation failures into one generic failure: rejected because callers need to distinguish invalid body shape, auth failures, channel access failures, quota failures, and unavailable-service cases.
- Log or echo full request bodies for diagnostics: rejected because channel metadata can contain sensitive values.

## Decision: Maintain constitution gates through TDD, full-suite validation, and docstrings

**Rationale**: The constitution requires contract-first design, Red-Green-Refactor, integration and regression coverage, full-suite validation after final code changes, and reStructuredText docstrings for every new or changed Python function. The plan therefore requires failing tests before implementation, focused checks during Green, cleanup plus `python3 -m pytest` and `python3 -m ruff check .` in Refactor, and docstrings for builders, validators, writable-part helpers, auth-context helpers, handlers, mappers, registration helpers, and examples.

**Alternatives considered**:

- Use only targeted tests: rejected because the constitution requires a full repository test-suite run after final code changes.
- Skip docstrings for small helpers: rejected because every new or changed Python function requires reStructuredText docstrings.
- Defer contracts until implementation: rejected because MCP-facing behavior must be contract-first.

## Sources

- Official `channels.update` reference: https://developers.google.com/youtube/v3/docs/channels/update
- Official quota calculator: https://developers.google.com/youtube/v3/determine_quota_cost
- Local Layer 1 dependency: `/Users/ctgunn/Projects/youtube-mcp-server/specs/111-channels-update-wrapper/`
- Local Layer 2 shared contracts: `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/`
