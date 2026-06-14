# Data Model: Layer 2 Tool `channelSections_delete`

## Entity: Channel Sections Delete Tool

**Description**: Public Layer 2 MCP tool representing one direct YouTube Data API `channelSections.delete` operation.

**Fields**

- `tool_name`: Constant string `channelSections_delete`.
- `upstream_resource`: Constant string `channelSections`.
- `upstream_method`: Constant string `delete`.
- `operation_key`: Constant string `channelSections.delete`.
- `quota_cost`: Constant integer `50`.
- `auth_mode`: Constant `oauth_required`.
- `availability_state`: Active unless official documentation changes.
- `input_contract`: JSON-compatible schema for the delete request.
- `response_convention`: Metadata describing deletion acknowledgment and optional upstream body preservation.
- `response_boundary`: Near-raw or lightly reshaped result boundary with explicit disallowed higher-level behaviors.
- `usage_notes` and `caveats`: Caller-facing text that includes quota, OAuth, partner, destructive deletion, no-body, and out-of-scope behavior.

**Relationships**

- Uses the Layer 1 `channelSections.delete` wrapper for endpoint execution.
- Is registered in the default MCP tool dispatcher.
- Is exported through `mcp_server.tools.youtube_common`.

**Validation Rules**

- Tool metadata must include quota cost `50` in description and usage notes.
- Tool metadata must not expose secrets, tokens, owner IDs, raw stack traces, or unsafe diagnostics.
- Tool must remain close to the upstream endpoint and not add lookup, repair, recovery, sorting, playlist cleanup, or bulk workflows.

## Entity: Channel Section Delete Request

**Description**: Caller-provided arguments for one delete operation.

**Fields**

- `id` (required string): Channel-section identifier to delete.
- `onBehalfOfContentOwner` (optional string): Partner-only delegation context for properly authorized content owners.

**Relationships**

- Produces exactly one Layer 1 `channelSections.delete` call when validation and OAuth checks pass.
- Produces a `Deletion Acknowledgment Result` on success or a shared Layer 2 error on failure.

**Validation Rules**

- `id` must be present, a string, and non-empty after trimming.
- `onBehalfOfContentOwner`, when present, must be a non-empty string and must require eligible OAuth partner authorization.
- No request body is accepted.
- Unsupported fields such as `part`, `body`, `ids`, `bulkDelete`, `cascade`, `playlistCleanup`, `recovery`, `undo`, `layoutRepair`, or channel update fields must be rejected before Layer 1 execution.

## Entity: Target Channel Section Identifier

**Description**: The upstream channel-section `id` query parameter.

**Fields**

- `value`: Non-empty string supplied as request `id`.

**Validation Rules**

- Missing, empty, non-string, malformed, or unsupported values return caller-facing `invalid_request` feedback.
- Upstream `idInvalid` maps to `invalid_request`.
- Upstream `idRequired` maps to `invalid_request`.
- Upstream `channelSectionNotFound` maps to `resource_not_found`.

## Entity: Partner Context

**Description**: Optional partner-only request context for content owners.

**Fields**

- `onBehalfOfContentOwner`: Optional non-empty string accepted as input.
- `public_result_flag`: Boolean `onBehalfOfContentOwner: true` when partner context was used.

**Validation Rules**

- Partner values must not be echoed in public results or errors.
- Empty partner values are rejected as `invalid_request`.
- Missing or ineligible OAuth for partner context returns `authentication_failed` or `authorization_failed` using shared Layer 2 conventions.

## Entity: Deletion Acknowledgment Result

**Description**: Public result returned after successful deletion.

**Fields**

- `endpoint`: Constant string `channelSections.delete`.
- `quotaCost`: Constant integer `50`.
- `deleted`: Boolean `true`.
- `delete`: Object with safe target context, at minimum `{ "id": "<requested id>" }`.
- `partnerContext`: Optional safe boolean flags for partner context.
- `upstream`: Optional preserved upstream response body when Layer 1 returns one.
- `bodyPolicy`: Optional marker such as `no_upstream_body` when the upstream response is empty.

**Validation Rules**

- Must not fabricate deleted resource fields.
- Must preserve safe upstream fields when a real upstream body is returned.
- Must not expose OAuth tokens, API keys, CMS owner identifiers, stack traces, or unsafe raw diagnostics.

## State Transitions

1. `Unvalidated Request` -> `Rejected` when required auth, identifier, partner context, or field-shape validation fails.
2. `Unvalidated Request` -> `Validated Request` when OAuth and argument checks pass.
3. `Validated Request` -> `Layer 1 Executed` after exactly one `channelSections.delete` wrapper call.
4. `Layer 1 Executed` -> `Deletion Acknowledged` when upstream deletion succeeds.
5. `Layer 1 Executed` -> `Mapped Error` when upstream returns quota, auth, invalid, missing-resource, unavailable, deprecated, or unexpected failure.
