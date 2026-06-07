# Data Model: YT-208 Layer 2 Tool `captions_delete`

## Captions Delete Tool

**Purpose**: Represents the public Layer 2 MCP tool that exposes the upstream `captions.delete` endpoint.

**Fields**:

- `tool_name`: Always `captions_delete`
- `upstream_resource`: Always `captions`
- `upstream_method`: Always `delete`
- `operation_key`: Stable identity `captions.delete`
- `quota_cost`: Official quota-unit cost `50`
- `auth_mode`: `oauth_required`
- `availability_state`: Active destructive caption-management operation, with OAuth and delegated-owner caveats visible
- `description`: Caller-facing discovery description that includes upstream identity, quota cost, auth summary, identifier requirement, destructive deletion summary, no-body rule, and delegation summary
- `input_schema`: Public request schema for required caption track `id` and optional delegation context
- `handler`: Callable behavior that validates, invokes the Layer 1 wrapper, and maps the result
- `usage_notes`: Caller-facing examples and quota/auth/deletion/delegation notes
- `response_boundary`: Near-raw endpoint-backed deletion acknowledgment result

**Validation Rules**:

- Must derive its name from `captions.delete` using the shared `resource_method` naming rule
- Must include quota cost `50` in metadata, description, and examples
- Must expose OAuth-required auth before invocation
- Must expose destructive deletion behavior before invocation
- Must expose required caption track `id` before invocation
- Must expose no-request-body behavior before invocation
- Must not include API keys, OAuth tokens, stack traces, signed URLs, raw private caption content, binary payloads, deleted-resource internals, or secret values in metadata, examples, errors, or logs
- Must remain a single-endpoint Layer 2 tool and must not add caption listing, caption creation, caption update, caption download, transcript summarization, deletion undo, recovery, language ranking, enrichment, translation, or cross-endpoint composition

**Relationships**:

- Owns one `Caption Delete Request`
- Produces one `Deletion Acknowledgment Result` or one `Captions Delete Error Outcome`
- Uses one Layer 1 `captions.delete` wrapper
- References one `Captions Delete Metadata Disclosure`

## Caption Delete Request

**Purpose**: Represents caller input for one `captions_delete` invocation.

**Fields**:

- `id`: Required caption track identifier.
- `onBehalfOfContentOwner`: Optional delegated content-owner context for eligible authorized callers.

**Validation Rules**:

- Must include non-empty `id`
- Must require eligible OAuth authorization
- Must reject missing OAuth authorization before endpoint execution
- Must validate delegated content-owner context without exposing credential details
- Must reject unsupported fields when the public schema disallows them
- Must not include a request body
- Must represent only one target caption track per request

**Relationships**:

- Uses one `Caption Track Identifier`
- Uses one `Permission Requirement`
- May include one `Delegation Context`
- Is validated before Layer 1 wrapper invocation

## Caption Track Identifier

**Purpose**: Identifies the specific caption track that should be deleted.

**Fields**:

- `id`: Non-empty caption track identifier as represented by a caption resource.

**Validation Rules**:

- Must be present for every request
- Must be non-empty
- Must not be replaced by video id, language, caption name, or inferred lookup state
- Must not expose private video-owner details beyond the safe identifier supplied by the caller

**Relationships**:

- Belongs to one `Caption Delete Request`
- Appears in safe operation context when useful
- May produce one `Captions Delete Error Outcome` for missing, invalid, inaccessible, or not-found caption tracks

## Permission Requirement

**Purpose**: Describes the credential and access expectation for caption deletion before invocation.

**Fields**:

- `auth_mode`: Always `oauth_required`
- `permission_note`: Caller-facing explanation that caption deletion requires eligible YouTube OAuth authorization
- `safe_error_category`: Shared error category when eligible authorization is missing or insufficient

**Validation Rules**:

- Must not present `captions_delete` as API-key-compatible
- Must not expose credential values, token names, or secret configuration details
- Must map missing eligible authorization to a stable caller-facing auth error
- Must distinguish insufficient deletion permission from invalid request shape or missing caption resource

**Relationships**:

- Applies to every `Caption Delete Request`
- Appears in `Captions Delete Metadata Disclosure`
- May produce one `Captions Delete Error Outcome`

## Delegation Context

**Purpose**: Represents optional content-owner delegation supplied by authorized callers.

**Fields**:

- `onBehalfOfContentOwner`: Optional content-owner identifier
- `authorization_note`: Caller-facing explanation that delegation still requires eligible OAuth authorization and linked CMS permissions

**Validation Rules**:

- Must be optional
- Must not be accepted as a substitute for OAuth authorization
- Must not expose delegated-owner secrets or credential details
- Must be preserved only as safe request context or metadata when useful

**Relationships**:

- May belong to one `Caption Delete Request`
- May appear as safe context in one `Deletion Acknowledgment Result`
- May produce one `Captions Delete Error Outcome` if authorization is missing or insufficient

## Deletion Acknowledgment Result

**Purpose**: Represents a successful near-raw deletion response from `captions_delete`.

**Fields**:

- `endpoint`: Upstream identity `captions.delete`
- `quotaCost`: Official quota-unit cost `50`
- `delete`: Safe summary of the caption track identity and mutation outcome
- `status`: Deletion acknowledgment state such as `deleted`
- `responseStatus`: Upstream success status context, expected to reflect HTTP `204 No Content`
- `hasResponseBody`: Boolean indicator expected to be false for the upstream success response
- `delegation`: Safe indication of whether delegation context was supplied when useful

**Validation Rules**:

- Must preserve deletion acknowledgment and operation context
- Must not fabricate deleted caption resource fields
- Must not include API keys, OAuth tokens, signed URLs, raw private caption content, binary payloads, deleted-resource internals, or secret values
- Must not expose raw private caption content in public examples, logs, or errors
- Must not add higher-level caption listing, caption creation, caption update, caption download, enrichment, recovery, or heuristic interpretation

**Relationships**:

- Produced by one valid `Caption Delete Request`
- References one `Captions Delete Metadata Disclosure`

## Captions Delete Error Outcome

**Purpose**: Represents a safe caller-facing failure for invalid requests, auth failures, quota failures, missing caption tracks, insufficient permissions, unavailable upstream service, or unexpected upstream failures.

**Fields**:

- `category`: Shared safe error category
- `message`: Caller-facing remediation-oriented message
- `details`: Safe request context such as tool name, invalid field, caption track id presence, delegation presence, destructive operation, or upstream operation

**Validation Rules**:

- Must not include stack traces, API keys, OAuth tokens, secret values, signed URLs, raw private caption content, binary payloads, deleted-resource internals, or sensitive owner credential details
- Must distinguish invalid identifier from unsupported request shape
- Must distinguish missing authorization from insufficient deletion permission
- Must distinguish missing caption tracks from invalid request shape
- Must preserve repeated deletion or already-missing targets as a safe not-found outcome unless upstream reports success
- Must preserve shared Layer 2 error categories where applicable

**Relationships**:

- Produced by one invalid or failed `Caption Delete Request`
- Uses shared YT-201/YT-202 error and safety conventions

## Captions Delete Metadata Disclosure

**Purpose**: Captures the pre-invocation metadata clients and reviewers need to understand the tool.

**Fields**:

- `name`: `captions_delete`
- `upstream`: `captions.delete`
- `quotaCost`: `50`
- `authMode`: `oauth_required`
- `availabilityState`: Active destructive deletion operation with OAuth and delegation caveats
- `inputContract`: Required `id`, optional delegation context, and no request body
- `responseBoundary`: Near-raw deletion acknowledgment response with light MCP clarity fields
- `usageNotes`: Examples for authorized deletion, delegated content-owner deletion, missing-identifier validation failure, invalid-identifier validation failure, unsupported option validation failure, repeated deletion or missing-resource failure, and authorization-sensitive failure

**Validation Rules**:

- Must be visible before invocation
- Must include quota, auth, identifier, destructive deletion, no-body, and delegation details in both structured metadata and caller-facing text
- Must describe delegated content-owner context
- Must explain no-content deletion acknowledgment response form
- Must stay free of credentials, stack traces, signed URLs, raw private caption content, binary payloads, deleted-resource internals, and secret values

**Relationships**:

- Describes one `Captions Delete Tool`
- Informs validation for every `Caption Delete Request`
- Informs review of every `Deletion Acknowledgment Result` and `Captions Delete Error Outcome`
