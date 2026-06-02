# Data Model: YT-206 Layer 2 Tool `captions_update`

## Captions Update Tool

**Purpose**: Represents the public Layer 2 MCP tool that exposes the upstream `captions.update` endpoint.

**Fields**:

- `tool_name`: Always `captions_update`
- `upstream_resource`: Always `captions`
- `upstream_method`: Always `update`
- `operation_key`: Stable identity `captions.update`
- `quota_cost`: Official quota-unit cost `450`
- `auth_mode`: `oauth_required`
- `availability_state`: Active media-capable mutation operation, with caption access, delegated-owner, and deprecated `sync` caveats visible
- `description`: Caller-facing discovery description that includes upstream identity, quota cost, auth summary, update-body summary, and optional media summary
- `input_schema`: Public request schema for `part`, caption update body, optional replacement media input, optional delegation context, and optional deprecated `sync` handling if supported
- `handler`: Callable behavior that validates, invokes the Layer 1 wrapper, and maps the result
- `usage_notes`: Caller-facing examples and quota/auth/update/media/delegation notes
- `response_boundary`: Near-raw endpoint-backed updated caption-resource result

**Validation Rules**:

- Must derive its name from `captions.update` using the shared `resource_method` naming rule
- Must include quota cost `450` in metadata, description, and examples
- Must expose OAuth-required auth before invocation
- Must expose the update-body requirement before invocation
- Must expose optional media-replacement behavior before invocation
- Must not include API keys, OAuth tokens, stack traces, signed URLs, raw media payloads, caption file contents, or secret values in metadata, examples, errors, or logs
- Must remain a single-endpoint Layer 2 tool and must not add transcript download, caption creation, language ranking, enrichment, translation, or cross-endpoint composition

**Relationships**:

- Owns one `Captions Update Request`
- Produces one `Updated Caption Resource Result` or one `Captions Update Error Outcome`
- Uses one Layer 1 `captions.update` wrapper
- References one `Captions Update Metadata Disclosure`

## Captions Update Request

**Purpose**: Represents caller input for one `captions_update` invocation.

**Fields**:

- `part`: Required comma-separated caption resource parts. The official update path supports `id` and `snippet`; `snippet` is used when updating draft status, while `id` applies when not updating draft status.
- `body`: Required caption resource update body.
- `media`: Optional replacement caption media descriptor or media input accepted by the public tool contract.
- `onBehalfOfContentOwner`: Optional delegated content-owner context for eligible authorized callers.
- `sync`: Deprecated optional upstream synchronization flag when supported by the implementation contract; processed upstream only when an updated caption file is supplied.

**Validation Rules**:

- Must include `part`
- Must include a supported caption update body
- Must include `body.id`
- Must require eligible OAuth authorization
- Must reject missing OAuth authorization before endpoint execution
- Must reject media-only requests without a valid update body
- Must reject unsupported fields when the public schema disallows them
- Must validate delegated content-owner context without exposing credential details
- Must treat `sync` as deprecated if it is accepted at all

**Relationships**:

- Uses one `Caption Update Body`
- May use one `Replacement Caption Media Input`
- Uses one `OAuth Requirement`
- May include one `Delegation Context`
- May include one `Deprecated Sync Option`
- Is validated before Layer 1 wrapper invocation

## Caption Update Body

**Purpose**: Represents the caption resource information required to update an existing caption track.

**Fields**:

- `id`: Required caption track identifier.
- `snippet.isDraft`: Optional draft-state flag when updating draft status.

**Validation Rules**:

- Must be present as an object
- Must include non-empty `id`
- Must preserve only supported writable caption fields in the public contract
- Must not include credential details or raw caption file contents
- Must remain metadata for one updated caption resource rather than a higher-level transcript workflow
- Must warn callers that omitting existing properties from an upstream update request can delete those existing property values when the endpoint applies full update semantics

**Relationships**:

- Belongs to one `Captions Update Request`
- Is preserved as safe operation context when useful
- May produce one `Captions Update Error Outcome` for missing or invalid update input

## Replacement Caption Media Input

**Purpose**: Represents optional uploaded caption track contents and safe media descriptor used when replacing caption content during an update.

**Fields**:

- `content`: Supported caption content representation or test-safe placeholder accepted by the implementation contract
- `mimeType`: Optional or required media MIME type, depending on the final schema
- `filename`: Optional safe filename or label when useful for diagnostics
- `sizeBytes`: Optional safe size descriptor for validation and review

**Validation Rules**:

- Must be optional for body-only draft-status or metadata updates
- Must not be accepted without a valid caption update body
- Must not expose raw caption file contents in public metadata, examples, errors, or logs
- Must respect the documented maximum file size and accepted MIME type caveats when those are enforced locally
- Must be represented safely in tests without real private caption content
- Must not trigger caption download or transcript extraction

**Relationships**:

- May belong to one `Captions Update Request`
- Affects the updated caption resource when supplied
- May produce one `Captions Update Error Outcome` for unsupported media input

## OAuth Requirement

**Purpose**: Describes the credential expectation for caption update before invocation.

**Fields**:

- `auth_mode`: Always `oauth_required`
- `scope_note`: Caller-facing explanation that caption update requires eligible YouTube OAuth authorization
- `safe_error_category`: Shared error category when eligible authorization is missing or insufficient

**Validation Rules**:

- Must not present `captions_update` as API-key-compatible
- Must not expose credential values, token names, or secret configuration details
- Must map missing eligible authorization to a stable caller-facing auth error
- Must distinguish insufficient update permission from invalid body or missing caption resource

**Relationships**:

- Applies to every `Captions Update Request`
- Appears in `Captions Update Metadata Disclosure`
- May produce one `Captions Update Error Outcome`

## Delegation Context

**Purpose**: Represents optional content-owner delegation supplied by authorized callers.

**Fields**:

- `onBehalfOfContentOwner`: Optional content-owner identifier
- `authorization_note`: Caller-facing explanation that delegation still requires eligible OAuth authorization

**Validation Rules**:

- Must be optional
- Must not be accepted as a substitute for OAuth authorization
- Must not expose delegated-owner secrets or credential details
- Must be preserved only as safe request context or metadata when useful

**Relationships**:

- May belong to one `Captions Update Request`
- May appear as safe context in one `Updated Caption Resource Result`
- May produce one `Captions Update Error Outcome` if authorization is missing or insufficient

## Deprecated Sync Option

**Purpose**: Represents the official but deprecated `sync` parameter when the public contract chooses to expose it.

**Fields**:

- `sync`: Optional boolean flag
- `deprecation_note`: Caller-facing warning that the option is deprecated and not the recommended path
- `media_requirement_note`: Caller-facing note that upstream processing of this parameter requires updated caption media

**Validation Rules**:

- Must not be required
- Must not be shown as the primary example
- Must be clearly marked deprecated wherever accepted
- Must not be accepted in a way that implies body-only automatic synchronization
- Must not add higher-level transcript alignment semantics beyond the upstream parameter

**Relationships**:

- May belong to one `Captions Update Request`
- Appears in `Captions Update Metadata Disclosure` as a caveat
- May produce one `Captions Update Error Outcome` if supplied without required media where the supported contract enforces that boundary

## Updated Caption Resource Result

**Purpose**: Represents a successful near-raw caption resource response from `captions_update`.

**Fields**:

- `item`: Returned caption resource or equivalent updated-resource payload
- `requestedParts`: Parts requested by the caller
- `endpoint`: Upstream identity `captions.update`
- `quotaCost`: Official quota-unit cost `450`
- `update`: Safe summary of the update body, including caption track identity and requested writable fields
- `media`: Safe summary of supplied media descriptor when replacement media is present, excluding raw content
- `delegation`: Safe indication of whether delegation context was supplied when useful

**Validation Rules**:

- Must preserve returned caption-resource fields from the endpoint-backed response
- Must preserve requested parts for review/debugging
- Must not fabricate missing upstream fields
- Must not include raw caption media content, credentials, or signed URLs
- Must not add higher-level language ranking, transcript lookup, enrichment, translation, or heuristic interpretation

**Relationships**:

- Produced by one valid `Captions Update Request`
- References one `Captions Update Metadata Disclosure`

## Captions Update Error Outcome

**Purpose**: Represents a safe caller-facing failure for invalid requests, auth failures, quota failures, missing caption tracks, insufficient permissions, media upload failures, unavailable upstream service, or unexpected upstream failures.

**Fields**:

- `category`: Shared safe error category
- `message`: Caller-facing remediation-oriented message
- `details`: Safe request context such as tool name, invalid field, body presence, media presence, delegation presence, or upstream operation

**Validation Rules**:

- Must not include stack traces, API keys, OAuth tokens, secret values, signed URLs, raw media payloads, caption file contents, or sensitive owner credential details
- Must distinguish invalid update body from unsupported media input
- Must distinguish missing authorization from insufficient update permission
- Must distinguish missing caption tracks from invalid request shape
- Must preserve shared Layer 2 error categories where applicable

**Relationships**:

- Produced by one invalid or failed `Captions Update Request`
- Uses shared YT-201/YT-202 error and safety conventions

## Captions Update Metadata Disclosure

**Purpose**: Captures the pre-invocation metadata clients and reviewers need to understand the tool.

**Fields**:

- `name`: `captions_update`
- `upstream`: `captions.update`
- `quotaCost`: `450`
- `authMode`: `oauth_required`
- `availabilityState`: Active media-capable mutation operation with caption-access, delegation, and deprecated-option caveats
- `inputContract`: Required `part`, required caption update body, optional replacement media input, optional delegation context, and deprecated `sync` caveat where supported
- `responseBoundary`: Near-raw updated caption-resource response with light MCP clarity fields
- `usageNotes`: Examples for authorized body-only update, authorized body-plus-media update, delegated content-owner context, missing-body validation failure, media-without-body validation failure, and authorization-sensitive failure

**Validation Rules**:

- Must be visible before invocation
- Must include quota, auth, update-body, and optional media-replacement details in both structured metadata and caller-facing text
- Must describe delegated content-owner context
- Must describe deprecated `sync` behavior if the parameter is accepted
- Must stay aligned with YT-201/YT-202 shared metadata standards

**Relationships**:

- Belongs to the `Captions Update Tool`
