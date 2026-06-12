# Data Model: YT-214 Layer 2 Tool `channelSections_update`

## Channel Sections Update Tool

**Purpose**: Public Layer 2 MCP tool named `channelSections_update` that exposes the upstream `channelSections.update` channel-section update operation.

**Fields**:

- `toolName`: Must be `channelSections_update`.
- `upstreamResource`: Must be `channelSections`.
- `upstreamMethod`: Must be `update`.
- `operationKey`: Must be `channelSections.update`.
- `quotaCost`: Must be `50`.
- `authMode`: Must be `oauth_required`.
- `availabilityState`: Should indicate active write availability with documented OAuth, partner-context, writable-field, overwrite, and content-structure caveats.
- `description`: Caller-facing description that includes endpoint identity, quota cost, OAuth requirement, required target section identity, and channel-section body requirement.
- `inputContract`: JSON-compatible schema for the channel-section update request.
- `responseConvention`: Updated-resource convention preserving returned channel-section fields.
- `responseBoundary`: Near-raw endpoint boundary with allowed safe wrapper fields.
- `usageNotes`: Caller-facing notes that include quota, OAuth, part selection, required body, required `body.id`, required `snippet.type`, writable fields, overwrite behavior, content-structure rules, partner context, and out-of-scope higher-level workflows.
- `caveats`: Safe caveats for owner-scoped write behavior, partner-only delegation, section-type-specific content behavior, overwrite-sensitive update behavior, and unsupported higher-level channel-section workflows.

**Validation Rules**:

- Tool name must derive from `channelSections.update` without adding a `youtube_` prefix.
- Quota cost must be visible in metadata, description, and usage notes.
- Auth mode must be OAuth required.
- Public metadata must not include credentials, stack traces, private channel data, CMS account details, owner identifiers, or secret values.
- The contract must remain scoped to channel-section updates and must not claim to perform section sorting, patch semantics, multi-section replacement, playlist creation, video metadata expansion, analytics, ranking, recommendation, branding, bulk editing, or enrichment.

**Relationships**:

- Uses the `Channel Section Update Request` as input.
- Produces a `Channel Section Update Result`.
- Depends on the YT-114 Layer 1 `channelSections.update` wrapper for endpoint execution.
- Follows YT-201 and YT-202 shared Layer 2 contract standards.

## Channel Section Update Request

**Purpose**: Caller-provided arguments for one `channelSections_update` invocation.

**Fields**:

- `part` (required): Comma-separated channel-section resource parts that identify properties being updated and returned.
- `body` (required): Channel-section resource body to update.
- `onBehalfOfContentOwner` (optional partner context): YouTube content-owner context intended exclusively for eligible content partners.

**Validation Rules**:

- `part` is required and must be non-empty.
- Officially documented update part values include `contentDetails`, `id`, and `snippet`.
- `body` is required and must be an object.
- `body.id` is required and must identify the existing channel section being updated.
- `body.snippet.type` is required.
- `body.snippet.title`, `body.snippet.position`, `body.contentDetails.playlists[]`, and `body.contentDetails.channels[]` are supported only where they match the selected section type.
- Requests requiring OAuth must fail safely when no eligible OAuth authorization is available.
- `onBehalfOfContentOwner` is partner-scoped and requires eligible OAuth authorization.
- Unsupported fields, channel update fields, playlist creation fields, analytics fields, video expansion fields, layout recommendation fields, sorting instructions, patch instructions, multi-section replacement instructions, and enrichment instructions are invalid for this tool.
- The request contract must warn that omitted existing writable properties can be deleted by upstream update behavior.

**Relationships**:

- Contains one `Part Selection`.
- Contains one `Target Channel Section Identifier`.
- Contains one `Writable Channel Section Body`.
- May contain one `Partner Context`.
- Is validated before calling the Layer 1 wrapper.

## Target Channel Section Identifier

**Purpose**: The caller-provided identity of the existing channel section that should be updated.

**Fields**:

- `body.id`: Existing channel-section identifier.

**Validation Rules**:

- Must be present in the submitted update body.
- Must be a non-empty string.
- Invalid IDs, non-editable sections, and missing target sections must surface safe caller-facing failures.

**Relationships**:

- Belongs to one `Channel Section Update Request`.
- Is preserved as safe operation context when returned by the endpoint.

## Part Selection

**Purpose**: Caller-selected channel-section resource sections that determine which fields are updated and returned.

**Fields**:

- `rawPart`: Original comma-separated part string.
- `requestedParts`: Ordered normalized part names with surrounding whitespace removed.

**Validation Rules**:

- Must be non-empty.
- Officially documented update values include `contentDetails`, `id`, and `snippet`.
- Unsupported part names are invalid for this public tool contract.
- Requested part names must be preserved for caller review.

**Relationships**:

- Belongs to one `Channel Section Update Request`.
- Is preserved in a `Channel Section Update Result`.

## Writable Channel Section Body

**Purpose**: Caller-provided channel-section resource content to update.

**Fields**:

- `id` (required): Existing section identifier.
- `snippet.type` (required): Section type controlling content requirements.
- `snippet.title` (conditional): Section title, required by some multi-content section types.
- `snippet.position` (optional): Requested section position when accepted by the endpoint.
- `contentDetails.playlists[]` (conditional): Playlist references for playlist-backed section types.
- `contentDetails.channels[]` (conditional): Channel references for channel-backed section types.

**Validation Rules**:

- `id` is required.
- `snippet` is required.
- `snippet.type` is required and must be non-empty.
- `singlePlaylist` requires exactly one playlist reference.
- `multiplePlaylists` requires playlist references and a title.
- `multipleChannels` requires channel references and a title.
- Playlist references are invalid for section types that do not expect playlists.
- Channel references are invalid for section types that do not expect channels.
- Duplicate playlist or channel references are invalid.
- Too many playlist or channel references must be rejected or mapped safely.
- Private playlists, missing playlists, inactive channels, missing channels, own-channel references, not-editable sections, invalid target IDs, and missing target sections must surface safe caller-facing failures when reported.
- Read-only fields and unsupported body fields are invalid.
- Omitted existing writable fields may be deleted by upstream update behavior and must be documented before invocation.

**Relationships**:

- Belongs to one `Channel Section Update Request`.
- Contains one `Writable Field Rule`.
- Contains one `Section Content Rule`.
- Produces one upstream-updated `Channel Section Update Result` when successful.

## Writable Field Rule

**Purpose**: The distinction between fields callers may update, fields that are read-only, and submitted fields that can replace or clear existing values.

**Fields**:

- `supportedFields`: `id`, `snippet.type`, `snippet.title`, `snippet.position`, `contentDetails.playlists[]`, and `contentDetails.channels[]`.
- `readOnlyFields`: Any returned resource fields that must not be accepted as writable input.
- `overwriteSensitive`: Boolean caveat indicating that omitted existing values can be deleted by upstream update behavior.

**Validation Rules**:

- Supported writable fields must match the endpoint contract.
- Unsupported or read-only fields must be rejected or clearly flagged.
- The overwrite-sensitive behavior must be discoverable before invocation.

**Relationships**:

- Is derived from one `Writable Channel Section Body`.
- Is documented in discovery metadata, contract examples, and quickstart.

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

- Is derived from one `Writable Channel Section Body`.
- Drives body validation and error mapping.

## Partner Context

**Purpose**: Optional caller-provided context used when an authorized YouTube content partner flow is supported for the update request.

**Fields**:

- `onBehalfOfContentOwner`: Partner owner identifier.
- `partnerScoped`: Safe boolean caveat indicating the request uses partner-only behavior.

**Validation Rules**:

- Partner context requires eligible OAuth authorization.
- `onBehalfOfContentOwner` must be non-empty when supplied.
- Public metadata, examples, errors, and logs must not expose real CMS account identifiers or private channel details.

**Relationships**:

- May belong to one `Channel Section Update Request`.
- May be echoed only as safe flags in `Channel Section Update Result`.

## Auth Requirement

**Purpose**: Caller-facing access expectation for channel-section updates.

**Fields**:

- `authMode`: `oauth_required`.
- `scopeGuidance`: Safe statement that eligible YouTube OAuth authorization is required.
- `partnerGuidance`: Safe statement that partner context requires eligible content-owner authorization.

**Validation Rules**:

- Missing OAuth must surface a safe authentication failure before write execution.
- Insufficient owner or partner authorization must surface a safe authorization failure.
- Errors must not expose OAuth tokens, API keys, private channel data, CMS account details, or secret values.

**Relationships**:

- Applies to every `Channel Section Update Request`.
- Is used by the handler before calling the Layer 1 wrapper.

## Channel Section Update Result

**Purpose**: Caller-facing result from a successful `channelSections_update` request.

**Fields**:

- `endpoint`: Safe operation identity such as `channelSections.update`.
- `quotaCost`: Official quota cost, `50`.
- `item`: Returned channel-section resource from the endpoint.
- `requestedParts`: Ordered normalized part names.
- `partnerContext`: Safe partner/delegation flags when applicable.
- `updated`: Boolean marker indicating the endpoint-backed update operation succeeded.

**Validation Rules**:

- Must preserve returned upstream channel-section fields.
- Must preserve selected parts and safe operation context.
- Must not fabricate missing optional fields.
- Must not expand playlists, channels, videos, analytics, rankings, recommendations, layout plans, patch state, deletion state, or enriched summaries.
- Must not expose credentials, private channel data beyond returned endpoint fields, stack traces, CMS account details, or secret values.

**Relationships**:

- Produced by `channelSections_update`.
- Contains one requested part summary.
- May contain safe partner context.

## Error Outcome

**Purpose**: Safe caller-facing representation of validation and upstream failures.

**Fields**:

- `category`: Shared Layer 2 error category.
- `message`: Caller-facing correction guidance.
- `details`: Safe diagnostic context, such as invalid field name, section type, target ID state, content rule, partner-context flag, or upstream status when safe.

**Validation Rules**:

- Missing `part`, unsupported part names, missing `body`, missing `body.id`, invalid `body.id`, missing `snippet`, missing `snippet.type`, invalid content structure, duplicate references, unsupported fields, unsupported optional parameters, and unsupported higher-level workflow fields map to safe invalid-request outcomes.
- Missing OAuth maps to a safe authentication failure.
- Insufficient owner or partner authorization maps to a safe authorization failure.
- Missing target sections or referenced playlists/channels map to safe resource-not-found outcomes.
- Not-editable sections, quota, unavailable service, deprecated behavior, content-rule, and unexpected upstream failures must follow shared Layer 2 error conventions.
- Errors must not expose stack traces, credentials, private channel data, CMS account details, owner identifiers, or secret values.

## State Transitions

1. **Discovered**: `channelSections_update` appears in the public tool catalog with full metadata.
2. **Validated**: Caller arguments satisfy part, body, target ID, section-type, content-rule, OAuth, partner-context, and overwrite-disclosure constraints.
3. **Update Attempted**: The request is routed to the Layer 1 `channelSections.update` wrapper.
4. **Succeeded**: The tool returns a near-raw `Channel Section Update Result` with returned resource fields, requested parts, safe partner context when present, and operation context.
5. **Rejected**: Invalid input or authorization-sensitive failures return a safe `Error Outcome`.
6. **Out of Scope**: Requests for section sorting, patching, multi-section replacement, playlist creation, video metadata expansion, analytics, layout recommendation, channel branding, bulk editing, or enrichment are rejected or documented as separate behavior.
