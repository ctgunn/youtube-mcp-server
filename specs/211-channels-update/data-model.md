# Data Model: YT-211 Layer 2 Tool `channels_update`

## Channels Update Tool

**Purpose**: Public Layer 2 MCP tool named `channels_update` that exposes the upstream `channels.update` channel metadata mutation operation.

**Fields**:

- `toolName`: Must be `channels_update`.
- `upstreamResource`: Must be `channels`.
- `upstreamMethod`: Must be `update`.
- `operationKey`: Must be `channels.update`.
- `quotaCost`: Must be `50`.
- `authMode`: Must be `oauth_required`.
- `availabilityState`: Should indicate active mutation availability with writable-part caveats.
- `description`: Caller-facing description that includes endpoint identity, quota cost, OAuth requirement, and writable-part requirement.
- `inputContract`: JSON-compatible schema for the update request.
- `responseConvention`: Mutation-result convention preserving returned channel resource fields.
- `responseBoundary`: Near-raw endpoint boundary with allowed safe wrapper fields.
- `usageNotes`: Caller-facing notes that include quota, OAuth, supported writable parts, part-to-body alignment, overwrite behavior, official content-owner delegation caveat, and banner upload boundary.
- `caveats`: Safe caveats for supported writable parts, read-only exclusions, one-part mutation behavior, and out-of-scope channel workflows.

**Validation Rules**:

- Tool name must derive from `channels.update` without adding a `youtube_` prefix.
- Quota cost must be visible in metadata, description, and usage notes.
- Auth mode must not imply API-key-only access.
- Public metadata must not include credentials, stack traces, raw private channel data, sensitive request-body values, or secret values.
- The contract must remain scoped to one endpoint-backed channel update and must not claim to upload banners, perform lookup, or orchestrate multi-step channel management.

**Relationships**:

- Uses the `Channels Update Request` as input.
- Produces an `Updated Channel Result`.
- Depends on the YT-111 Layer 1 `channels.update` wrapper for endpoint execution.
- Follows YT-201 and YT-202 shared Layer 2 contract standards.

## Channels Update Request

**Purpose**: Caller-provided arguments for one `channels_update` invocation.

**Fields**:

- `part` (required): One selected writable channel part.
- `body` (required): Channel resource payload containing target channel identity and fields aligned to the selected part.

**Validation Rules**:

- `part` is required and must identify exactly one supported writable part for this slice.
- Supported writable parts are `brandingSettings` and `localizations`.
- `body` is required and must be a non-empty object.
- `body.id` is required to identify the target channel.
- The selected `part` must have a matching top-level field in `body`.
- Unsupported parts, read-only fields, missing body fields, part-to-body mismatches, and unexpected top-level request fields must be rejected before endpoint execution.
- `onBehalfOfContentOwner` is not part of this slice's public input contract unless the YT-111 Layer 1 dependency is intentionally expanded first.

**Relationships**:

- Contains one `Writable Channel Part`.
- Contains one `Channel Body`.
- Requires one `Access Context`.
- Is validated before calling the Layer 1 wrapper.

## Writable Channel Part

**Purpose**: Caller-selected channel resource area that this slice permits the tool to update.

**Fields**:

- `partName`: Supported value such as `brandingSettings` or `localizations`.
- `supportedState`: Whether the part is supported by this feature scope.
- `bodyField`: Matching field that must be present in the channel body.
- `readOnlyExclusions`: Fields that must not be treated as writable for the selected part.
- `overwriteWarning`: Caller-facing note that updating a part can replace mutable values in that part.

**Validation Rules**:

- Exactly one supported part may be active for a public request.
- The matching channel body field is required.
- Unsupported official or future parts must be rejected or documented as outside this slice until the Layer 1 dependency supports them.
- Read-only or unrelated channel fields must not be silently accepted or dropped.

**Relationships**:

- Belongs to a `Channels Update Request`.
- Controls validation of the `Channel Body`.
- Is reflected in the `Updated Channel Result`.

## Channel Body

**Purpose**: Channel resource payload supplied for one supported update.

**Fields**:

- `id`: Target channel identifier.
- `brandingSettings`: Writable branding settings when `part` is `brandingSettings`.
- `localizations`: Writable localization map when `part` is `localizations`.

**Validation Rules**:

- Must be a non-empty object.
- `id` must be present and non-empty.
- Must contain the field that matches the selected writable part.
- Must not contain read-only or unsupported top-level channel fields for this slice.
- May include banner URL activation content through `brandingSettings.image.bannerExternalUrl`, but must not include raw banner media or upload instructions.

**Relationships**:

- Belongs to a `Channels Update Request`.
- Is validated against the selected `Writable Channel Part`.
- Feeds the Layer 1 `channels.update` wrapper.

## Access Context

**Purpose**: The caller's authorization and channel-management eligibility for the requested update.

**Fields**:

- `authMode`: Must be OAuth-required.
- `oauthAvailable`: Whether eligible OAuth authorization is available.
- `channelManagementEligibility`: Whether the authorized caller can update the target channel.
- `failureBoundary`: Expected distinction between missing auth, insufficient channel access, invalid request shape, and upstream failure.

**Validation Rules**:

- Public API-key-only access is unsupported.
- Missing OAuth must fail before endpoint execution.
- Insufficient channel-management eligibility must remain distinguishable from malformed request bodies.
- Credentials, tokens, and private user details must not appear in public metadata, examples, errors, or logs.

**Relationships**:

- Required by `Channels Update Request`.
- Is accompanied by the `Content-Owner Delegation Caveat`.
- Interprets success or failure of `Updated Channel Result`.

## Content-Owner Delegation Caveat

**Purpose**: Maintainer-facing note that official `channels.update` documentation includes content-owner delegation, while this public Layer 2 slice does not expose that field unless the YT-111 Layer 1 wrapper is intentionally expanded first.

**Fields**:

- `officialField`: `onBehalfOfContentOwner`.
- `supportState`: Out of scope for this slice unless the dependency changes.
- `reason`: The current public tool relies on the existing YT-111 wrapper contract rather than defining a separate upstream request shape.

**Validation Rules**:

- Public input validation must reject `onBehalfOfContentOwner` while it is outside this slice.
- Caller-facing notes must identify the official-doc caveat without implying support.
- Any future support must keep delegation authorization-sensitive and must not substitute for eligible OAuth authorization.

**Relationships**:

- Documented by `Channels Update Tool`.
- Applies to `Channels Update Request` validation.

## Updated Channel Result

**Purpose**: Caller-facing result from a successful `channels_update` mutation.

**Fields**:

- `endpoint`: Safe operation identity such as `channels.update`.
- `quotaCost`: Official quota cost, `50`.
- `item` or `resource`: Near-raw returned channel resource fields.
- `updatedPart`: Selected writable part for the request.
- `requestedParts`: Safe normalized part list.

**Validation Rules**:

- Must preserve returned upstream channel resource fields when present.
- Must include safe operation context such as endpoint identity and quota cost.
- Must reflect selected writable part without echoing sensitive request body values unnecessarily.
- Must not fabricate channel analytics, lookup results, banner upload state, video expansion, playlist expansion, or higher-level channel-management state.

**Relationships**:

- Produced by `channels_update`.
- Interpreted alongside `Access Context`.
- May reflect a banner URL activation only as part of the returned channel resource.

## Error Outcome

**Purpose**: Safe caller-facing representation of validation and upstream failures.

**Fields**:

- `category`: Shared Layer 2 error category.
- `message`: Caller-facing correction guidance.
- `details`: Safe diagnostic context, such as invalid field name or upstream status when safe.

**Validation Rules**:

- Missing `part`, missing `body`, missing `body.id`, unsupported parts, multiple parts, part-to-body mismatches, read-only fields, unsupported top-level fields, and unsupported delegation fields map to safe invalid-request outcomes.
- Missing OAuth maps to a safe authentication failure.
- Insufficient channel-management access maps to a safe authorization failure.
- Upstream branding/localization validation, quota, missing channel, unavailable service, and unexpected failures must follow shared Layer 2 error conventions.
- Errors must not expose stack traces, credentials, private channel data, raw sensitive request bodies, or secret values.

## State Transitions

1. **Discovered**: `channels_update` appears in the public tool catalog with full metadata.
2. **Validated**: Caller arguments satisfy part, body, and OAuth constraints.
3. **Update Attempted**: The request is routed to the Layer 1 `channels.update` wrapper.
4. **Succeeded**: The tool returns a near-raw `Updated Channel Result` with returned resource fields and safe operation context.
5. **Rejected**: Invalid input or authorization-sensitive failures return a safe `Error Outcome`.
6. **Out of Scope**: Requests to look up channels, upload banners, expand videos/playlists, analyze channels, or orchestrate multi-step channel management are rejected or documented as separate behavior.
