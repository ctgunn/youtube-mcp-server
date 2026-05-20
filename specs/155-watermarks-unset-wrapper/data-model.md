# Data Model: YT-155 Layer 1 Endpoint `watermarks.unset`

## Watermarks Unset Wrapper Contract

**Purpose**: Describes the internal Layer 1 wrapper for `watermarks.unset` in a way that exposes endpoint identity, quota cost, supported removal-request boundaries, authorization expectations, no-upload behavior, and normalized watermark-removal acknowledgement rules before implementation details are inspected.

**Fields**:

- `resource_name`: Upstream resource name, expected to remain `watermarks`
- `operation_name`: Upstream operation name, expected to remain `unset`
- `operation_key`: Stable internal operation key, expected to remain `watermarks.unset`
- `http_method`: Mutation request method, expected to be `POST`
- `path_shape`: Endpoint path shape, expected to represent `/youtube/v3/watermarks/unset`
- `quota_cost`: Official quota-unit cost, expected to be `50`
- `auth_mode`: Required access mode, expected to be `oauth_required`
- `request_shape`: Maintainer-visible declaration of required and optional request fields
- `notes`: Maintainer-facing guidance for required `channelId`, no media-upload input, optional partner-only delegation, unsupported request shapes, no-removal-possible outcomes, and failure boundaries

**Validation Rules**:

- Must identify `watermarks.unset` consistently across metadata, docs, contracts, and review surfaces
- Must expose quota cost `50` wherever endpoint metadata is reviewed
- Must expose OAuth-required access expectations
- Must identify `channelId` as the required supported input
- Must document that watermark metadata and media upload fields are outside the supported unset contract
- Must document that successful execution is represented as a watermark-removal acknowledgement rather than a returned watermark resource
- Must document that unsupported modifiers are outside the supported boundary unless explicitly added to the wrapper contract

**Relationships**:

- Defines the contract used by `Watermark Unset Request`
- Produces or classifies `Watermark Removal Acknowledgement` and `Watermark Removal Failure Outcome`
- Feeds downstream review surfaces and higher-layer summaries without introducing a public MCP tool in this slice

## Watermark Unset Request

**Purpose**: Represents one supported request to remove a YouTube channel watermark through the internal Layer 1 wrapper.

**Fields**:

- `channelId`: Required target YouTube channel identifier
- `onBehalfOfContentOwner`: Optional partner-only delegated content-owner context if, and only if, the final wrapper contract deliberately supports it

**Validation Rules**:

- `channelId` is required
- `channelId` must be a non-empty string after trimming surrounding whitespace
- `body`, `media`, watermark timing, watermark position, and upload-specific fields are unsupported for this unset contract
- Requests with blank, missing, malformed, or unsupported channel fields must be rejected or clearly flagged before execution when determinable locally
- Unsupported top-level fields must be rejected or clearly flagged rather than silently forwarded
- Partner-only delegation must either be explicitly supported and documented or clearly flagged as outside the guaranteed boundary
- A valid request still requires OAuth-backed access and may still fail because of ownership, permissions, policy state, channel availability, current watermark state, or upstream conditions

**Relationships**:

- Valid requests are evaluated against `Watermarks Unset Wrapper Contract`
- Successful execution produces `Watermark Removal Acknowledgement`
- Invalid, unauthorized, unsupported, no-removal-possible, or refused execution produces `Watermark Removal Failure Outcome`

## Watermark Removal Acknowledgement

**Purpose**: Represents the normalized success result for an accepted `watermarks.unset` request, including enough context for downstream layers to know what was removed without requiring an upstream response body.

**Fields**:

- `is_unset` or equivalent acknowledgement flag: Indicates the watermark-unset request was accepted as successful
- `channel_id`: Target channel identifier from the accepted request
- `source_operation`: Expected to remain `watermarks.unset`
- `source_auth_mode`: Expected to remain `oauth_required`
- `source_quota_cost`: Expected to remain `50`
- `source_required_fields`: Expected to include `channelId`
- `source_notes`: Review guidance from wrapper metadata

**Validation Rules**:

- Must not include OAuth tokens, credentials, secret-backed values, or unrelated watermark media data
- Must not expose channel owner identity unless a later contract explicitly requires and protects it
- Must remain distinguishable from validation failures, authorization failures, unsupported-payload outcomes, no-removal-possible outcomes, upstream refusal outcomes, and upstream unavailability
- Must preserve enough target context for downstream layers to identify the acknowledged watermark removal

**State Transitions**:

- `requested` -> `acknowledged` when a valid authorized request succeeds
- `requested` -> `no_removal_possible` when the target channel has no removable watermark or upstream reports an already-removed/not-found state
- `requested` -> `failed` when local validation, authorization, unsupported payload, or upstream execution fails

## Watermark Removal Failure Outcome

**Purpose**: Represents one normalized non-success outcome from a `watermarks.unset` request so downstream callers can distinguish what kind of remediation is needed.

**Fields**:

- `category`: Failure classification such as `invalid_request`, access-related failure, `forbidden`, `not_found`, `no_removal_possible`, or `upstream_unavailable`
- `message`: Maintainer-safe failure description
- `status_code`: Upstream status code when execution reached the upstream service
- `channel_id`: Target channel identifier when safe and available
- `source_operation`: Expected to remain `watermarks.unset`

**Validation Rules**:

- Missing or malformed `channelId` must be classified separately from access and upstream failures
- Unsupported `body`, `media`, watermark metadata, or upload fields must remain distinguishable from missing channel context
- Missing or incompatible OAuth-backed access must be classified separately from malformed input
- Forbidden channel failures must remain distinguishable from no-removal-possible outcomes
- No-current-watermark, already-removed, or not-found outcomes must remain distinguishable from successful watermark-removal acknowledgements
- Transient upstream failures must remain distinguishable from caller-correctable request errors
- Sensitive credentials, tokens, and unrelated media content must never appear in failure outcomes

**Relationships**:

- Produced from invalid `Watermark Unset Request` inputs or from normalized upstream execution failures
- Used by tests and higher-layer summaries to preserve actionable failure boundaries
