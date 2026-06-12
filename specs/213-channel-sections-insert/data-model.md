# Data Model: YT-213 Layer 2 Tool `channelSections_insert`

## Channel Sections Insert Tool

**Purpose**: Public Layer 2 MCP tool named `channelSections_insert` that exposes the upstream `channelSections.insert` channel-section creation operation.

**Fields**:

- `toolName`: Must be `channelSections_insert`.
- `upstreamResource`: Must be `channelSections`.
- `upstreamMethod`: Must be `insert`.
- `operationKey`: Must be `channelSections.insert`.
- `quotaCost`: Must be `50`.
- `authMode`: Must be `oauth_required`.
- `availabilityState`: Should indicate active write availability with documented OAuth, partner-context, content-structure, and section-limit caveats.
- `description`: Caller-facing description that includes endpoint identity, quota cost, OAuth requirement, and channel-section body requirement.
- `inputContract`: JSON-compatible schema for the channel-section create request.
- `responseConvention`: Created-resource convention preserving returned channel-section fields.
- `responseBoundary`: Near-raw endpoint boundary with allowed safe wrapper fields.
- `usageNotes`: Caller-facing notes that include quota, OAuth, part selection, required body, required `snippet.type`, content-structure rules, partner context, section limit, and out-of-scope higher-level workflows.
- `caveats`: Safe caveats for owner-scoped write behavior, partner-only delegation, section-type-specific content rules, maximum section behavior, and unsupported higher-level channel-section workflows.

**Validation Rules**:

- Tool name must derive from `channelSections.insert` without adding a `youtube_` prefix.
- Quota cost must be visible in metadata, description, and usage notes.
- Auth mode must be OAuth required.
- Public metadata must not include credentials, stack traces, private channel data, CMS account details, owner identifiers, or secret values.
- The contract must remain scoped to channel-section creation and must not claim to perform section sorting, replacement, playlist creation, video metadata expansion, analytics, ranking, recommendation, branding, bulk editing, or enrichment.

**Relationships**:

- Uses the `Channel Section Create Request` as input.
- Produces a `Channel Section Create Result`.
- Depends on the YT-113 Layer 1 `channelSections.insert` wrapper for endpoint execution.
- Follows YT-201 and YT-202 shared Layer 2 contract standards.

## Channel Section Create Request

**Purpose**: Caller-provided arguments for one `channelSections_insert` invocation.

**Fields**:

- `part` (required): Comma-separated channel-section resource parts that identify properties being written and returned.
- `body` (required): Channel-section resource body to create.
- `onBehalfOfContentOwner` (optional partner context): YouTube content-owner context intended exclusively for eligible content partners.
- `onBehalfOfContentOwnerChannel` (optional partner context): Channel ID paired with `onBehalfOfContentOwner` for eligible delegated-channel requests.

**Validation Rules**:

- `part` is required and must be non-empty.
- Officially documented insert part values include `contentDetails`, `id`, and `snippet`.
- `body` is required and must be an object.
- `body.snippet.type` is required.
- `body.snippet.title`, `body.snippet.position`, `body.contentDetails.playlists[]`, and `body.contentDetails.channels[]` are supported only where they match the selected section type.
- Requests requiring OAuth must fail safely when no eligible OAuth authorization is available.
- `onBehalfOfContentOwnerChannel` requires `onBehalfOfContentOwner`.
- `onBehalfOfContentOwner` with no paired channel context must be rejected or clearly flagged according to the supported partner contract for this slice.
- Unsupported fields, channel update fields, playlist creation fields, analytics fields, video expansion fields, layout recommendation fields, sorting instructions, and enrichment instructions are invalid for this tool.

**Relationships**:

- Contains one `Part Selection`.
- Contains one `Channel Section Body`.
- May contain one `Partner or Delegated-Channel Context`.
- Is validated before calling the Layer 1 wrapper.

## Part Selection

**Purpose**: Caller-selected channel-section resource sections that determine which fields are written and returned.

**Fields**:

- `rawPart`: Original comma-separated part string.
- `requestedParts`: Ordered normalized part names with surrounding whitespace removed.

**Validation Rules**:

- Must be non-empty.
- Officially documented insert values include `contentDetails`, `id`, and `snippet`.
- Unsupported part names are invalid for this public tool contract.
- Requested part names must be preserved for caller review.

**Relationships**:

- Belongs to one `Channel Section Create Request`.
- Is preserved in a `Channel Section Create Result`.

## Channel Section Body

**Purpose**: Caller-provided channel-section resource content to create.

**Fields**:

- `snippet.type` (required): Section type controlling content requirements.
- `snippet.title` (conditional): Section title, required by some multi-content section types.
- `snippet.position` (optional): Requested section position when accepted by the endpoint.
- `contentDetails.playlists[]` (conditional): Playlist references for playlist-backed section types.
- `contentDetails.channels[]` (conditional): Channel references for channel-backed section types.

**Validation Rules**:

- `snippet` is required.
- `snippet.type` is required and must be non-empty.
- `singlePlaylist` requires exactly one playlist reference.
- `multiplePlaylists` requires playlist references and a title.
- `multipleChannels` requires channel references and a title.
- Playlist references are invalid for section types that do not expect playlists.
- Channel references are invalid for section types that do not expect channels.
- Duplicate playlist or channel references are invalid.
- Too many playlist or channel references must be rejected or mapped safely.
- Private playlists, missing playlists, inactive channels, missing channels, and own-channel references must surface safe caller-facing failures when reported.
- Read-only fields and unsupported body fields are invalid.

**Relationships**:

- Belongs to one `Channel Section Create Request`.
- Contains one `Section Content Rule`.
- Produces one upstream-created `Channel Section Create Result` when successful.

## Section Content Rule

**Purpose**: The relationship between the selected section type and required or forbidden content details.

**Fields**:

- `sectionType`: Value from `body.snippet.type`.
- `requiredContentKind`: Playlist references, channel references, none, or endpoint-defined behavior.
- `requiresTitle`: Whether a title is required for the selected section type.
- `referenceLimitState`: Whether the number of references is valid, too high, duplicated, or unavailable.

**Validation Rules**:

- The selected section type controls whether playlist references, channel references, title, or content details are expected.
- Content details required by the section type must be present.
- Content details forbidden by the section type must not be present.
- Local validation should catch deterministic body-shape errors before endpoint execution.
- Resource-state failures discovered upstream must be mapped to safe Layer 2 error categories.

**Relationships**:

- Is derived from one `Channel Section Body`.
- Drives body validation and error mapping.

## Partner or Delegated-Channel Context

**Purpose**: Optional caller-provided context used when an authorized YouTube content partner flow is supported for the create request.

**Fields**:

- `onBehalfOfContentOwner`: Partner owner identifier.
- `onBehalfOfContentOwnerChannel`: Channel identifier paired with the owner context.
- `partnerScoped`: Safe boolean caveat indicating the request uses partner-only behavior.

**Validation Rules**:

- Partner context requires eligible OAuth authorization.
- `onBehalfOfContentOwnerChannel` can only be used with `onBehalfOfContentOwner`.
- When `onBehalfOfContentOwner` is present, the paired channel context must be present for delegated-channel insertion.
- Public metadata, examples, errors, and logs must not expose real CMS account identifiers or private channel details.

**Relationships**:

- May belong to one `Channel Section Create Request`.
- May be echoed only as safe flags in `Channel Section Create Result`.

## Auth Requirement

**Purpose**: Caller-facing access expectation for channel-section creation.

**Fields**:

- `authMode`: `oauth_required`.
- `scopeGuidance`: Safe statement that eligible YouTube OAuth authorization is required.
- `partnerGuidance`: Safe statement that partner context requires eligible content-owner authorization.

**Validation Rules**:

- Missing OAuth must surface a safe authentication failure before write execution.
- Insufficient owner or partner authorization must surface a safe authorization failure.
- Errors must not expose OAuth tokens, API keys, private channel data, CMS account details, or secret values.

**Relationships**:

- Applies to every `Channel Section Create Request`.
- Is used by the handler before calling the Layer 1 wrapper.

## Channel Section Create Result

**Purpose**: Caller-facing result from a successful `channelSections_insert` request.

**Fields**:

- `endpoint`: Safe operation identity such as `channelSections.insert`.
- `quotaCost`: Official quota cost, `50`.
- `item`: Returned channel-section resource from the endpoint.
- `requestedParts`: Ordered normalized part names.
- `partnerContext`: Safe partner/delegation flags when applicable.
- `created`: Boolean marker indicating the endpoint-backed create operation succeeded.

**Validation Rules**:

- Must preserve returned upstream channel-section fields.
- Must preserve selected parts and safe operation context.
- Must not fabricate missing optional fields.
- Must not expand playlists, channels, videos, analytics, rankings, recommendations, layout plans, update state, or enriched summaries.
- Must not expose credentials, private channel data beyond returned endpoint fields, stack traces, CMS account details, or secret values.

**Relationships**:

- Produced by `channelSections_insert`.
- Contains one requested part summary.
- May contain safe partner context.

## Error Outcome

**Purpose**: Safe caller-facing representation of validation and upstream failures.

**Fields**:

- `category`: Shared Layer 2 error category.
- `message`: Caller-facing correction guidance.
- `details`: Safe diagnostic context, such as invalid field name, section type, content rule, partner-context flag, or upstream status when safe.

**Validation Rules**:

- Missing `part`, unsupported part names, missing `body`, missing `snippet`, missing `snippet.type`, invalid content structure, duplicate references, unsupported fields, unsupported optional parameters, invalid partner context, and unsupported higher-level workflow fields map to safe invalid-request outcomes.
- Missing OAuth maps to a safe authentication failure.
- Insufficient owner or partner authorization maps to a safe authorization failure.
- Missing referenced playlists/channels map to safe resource-not-found outcomes.
- Quota, unavailable service, deprecated behavior, content-rule, capacity, and unexpected upstream failures must follow shared Layer 2 error conventions.
- Errors must not expose stack traces, credentials, private channel data, CMS account details, owner identifiers, or secret values.

## State Transitions

1. **Discovered**: `channelSections_insert` appears in the public tool catalog with full metadata.
2. **Validated**: Caller arguments satisfy part, body, section-type, content-rule, OAuth, and partner-context constraints.
3. **Create Attempted**: The request is routed to the Layer 1 `channelSections.insert` wrapper.
4. **Succeeded**: The tool returns a near-raw `Channel Section Create Result` with returned resource fields, requested parts, safe partner context when present, and operation context.
5. **Rejected**: Invalid input or authorization-sensitive failures return a safe `Error Outcome`.
6. **Out of Scope**: Requests for section sorting, section replacement, playlist creation, video metadata expansion, analytics, layout recommendation, channel branding, bulk editing, or enrichment are rejected or documented as separate behavior.
