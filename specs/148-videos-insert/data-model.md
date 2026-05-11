# Data Model: YT-148 Layer 1 Endpoint `videos.insert`

## Entity: Videos Insert Wrapper Contract

**Purpose**: Describes the internal Layer 1 wrapper for `videos.insert` in a way that exposes endpoint identity, quota cost, supported creation inputs, upload-mode guidance, authorization expectations, and visibility caveats before execution.

**Fields**:

- `resource_name`: Upstream resource name, expected to remain `videos`
- `operation_name`: Upstream operation name, expected to remain `insert`
- `operation_key`: Stable combined identifier used in tests and review surfaces
- `http_method`: Upstream HTTP method for the wrapper
- `path_shape`: Upstream path or route pattern for the wrapper
- `request_shape`: Allowed request fields for the wrapper contract
- `auth_mode`: Stable auth mode for this endpoint, expected to remain OAuth-required
- `quota_cost`: Official quota-unit cost of `1600`
- `notes`: Optional maintainer-facing notes for upload behavior, quota sensitivity, or visibility caveats
- `upload_mode_note`: Maintainer-facing explanation of how supported standard and resumable upload paths fit within the wrapper contract
- `visibility_caveat_note`: Maintainer-facing explanation of audit-related or private-default behavior that may affect the created video's initial visibility

**Validation Rules**:

- `resource_name`, `operation_name`, `http_method`, `path_shape`, `request_shape`, `auth_mode`, and `quota_cost` are required
- `quota_cost` must equal the official endpoint cost captured for this slice
- `auth_mode` must remain reviewable as OAuth-required rather than hiding access expectations in runtime-only behavior
- The wrapper contract is incomplete if upload requirements, upload-mode guidance, or visibility caveats are not visible in maintainer-facing artifacts

**Relationships**:

- Uses one `Video Creation Request`
- References one `Authorization Expectation`
- References one `Upload Mode Guidance`
- Produces one `Created Video Result`
- Is exercised through the shared executor and representative wrapper flow under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`

## Entity: Video Creation Request

**Purpose**: Represents one supported `videos.insert` request shape that combines reviewable metadata with upload content for video creation.

**Fields**:

- `part`: Requested resource parts or write scope for the creation call
- `body`: Video metadata payload that identifies what is being created
- `media`: Video upload payload submitted for the creation request
- `upload_mode`: Maintainer-facing label that distinguishes the supported standard-upload and resumable-upload paths
- `delegation_context`: Optional delegated owner context when authorized use requires it
- `request_mode`: Maintainer-facing label that distinguishes a valid create request from unsupported incomplete shapes

**Validation Rules**:

- A supported creation request must include `part`, one stable `body` metadata field, and one stable `media` upload field
- Metadata-only requests are invalid
- Upload-only requests are invalid
- Unsupported or unexpected fields must be rejected or clearly flagged before execution
- Delegation context, if supported, must remain optional and must not replace the base OAuth requirement

**Relationships**:

- Belongs to one `Videos Insert Wrapper Contract`
- Requires one `Authorization Expectation`
- Is interpreted through one `Upload Mode Guidance`
- Produces one `Created Video Result`

## Entity: Upload Mode Guidance

**Purpose**: Describes how the wrapper communicates the supported video-upload paths and what follow-up expectations apply to each path.

**Fields**:

- `supports_standard_upload`: Whether the wrapper supports a direct media upload path
- `supports_resumable_upload`: Whether the wrapper supports a resumable upload path
- `required_inputs`: Inputs that remain mandatory regardless of upload mode
- `follow_up_expectations`: Reviewable guidance for any additional resumable-upload continuation behavior
- `maintainer_note`: Explanation shown in metadata and contract artifacts

**Validation Rules**:

- At least one upload mode must be documented
- Any supported upload mode must preserve the same base metadata-plus-upload boundary
- Resumable-upload guidance must remain visible to maintainers before reuse

**Relationships**:

- Attached to one `Videos Insert Wrapper Contract`
- Referenced by one `Video Creation Request`

## Entity: Authorization Expectation

**Purpose**: Describes the credential and delegation requirement for one `videos.insert` request path.

**Fields**:

- `auth_mode`: The runtime auth selection compatible with the endpoint
- `requires_authorized_access`: Whether the request needs authorized access
- `delegation_input`: Optional delegated owner field visible to maintainers
- `maintainer_note`: Explanation shown in metadata and contract artifacts

**Validation Rules**:

- Supported `videos.insert` paths must require authorized access
- Delegation guidance, if present, must remain distinguishable from the base auth requirement
- Credential payloads must never be exposed in contract artifacts or documentation

**Relationships**:

- Applied to one `Videos Insert Wrapper Contract`
- Referenced by creation-request semantics and implementation tests

## Entity: Created Video Result

**Purpose**: Represents the successful outcome of a valid `videos.insert` request.

**Fields**:

- `resource_id`: Stable identifier for the created video
- `resource_parts`: The created video fields returned for the requested parts
- `creation_state`: Successful creation state visible to higher layers
- `upload_mode`: The validated upload mode used for the call
- `delegation_context_present`: Whether delegated owner context was supplied
- `visibility_state_note`: Reviewable note describing whether audit or private-default behavior affects the created video's initial visibility
- `metadata_visibility`: Whether quota, auth, upload guidance, and visibility caveats remain attached to the wrapper rather than being lost in the result payload

**Validation Rules**:

- A valid create request must end as either a created-video success or a normalized upstream failure
- Successful creation must not erase the wrapper's documented auth, upload, or visibility context
- Result handling must keep quota and source-operation visibility available to higher layers

**Relationships**:

- Returned by one `Videos Insert Wrapper Contract`
- Produced through the shared executor success path

## State Transitions

### Wrapper Review Lifecycle

1. `draft`: Endpoint metadata exists but upload guidance or visibility caveats may still be implicit
2. `reviewable`: Endpoint identity, quota cost, OAuth requirement, supported creation inputs, upload modes, and visibility caveats are visible together
3. `validated`: Unit, contract, integration, and transport checks prove metadata-plus-upload validation, OAuth-only guidance, upload-mode visibility, and created-video handling
4. `reusable`: Later video-creation work can consume the wrapper contract without extra endpoint research

### Request Outcome Lifecycle

1. Caller supplies one supported create-request shape
2. Wrapper validates required metadata, required upload input, allowed delegation input, and unexpected-field rejection
3. Shared executor runs with authorized access for the validated creation request
4. Request ends as one of `created video`, `policy-related upstream refusal`, or `normalized upstream failure`
