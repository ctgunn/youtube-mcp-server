# Data Model: YT-154 Layer 1 Endpoint `watermarks.set`

## Watermarks Set Wrapper Contract

**Purpose**: Describes the internal Layer 1 wrapper for `watermarks.set` in a way that exposes endpoint identity, quota cost, supported upload-request boundaries, authorization expectations, and normalized watermark-update acknowledgement rules before implementation details are inspected.

**Fields**:

- `resource_name`: Upstream resource name, expected to remain `watermarks`
- `operation_name`: Upstream operation name, expected to remain `set`
- `operation_key`: Stable internal operation key, expected to remain `watermarks.set`
- `http_method`: Upload mutation request method, expected to be `POST`
- `path_shape`: Endpoint path shape, expected to represent `/upload/youtube/v3/watermarks/set`
- `quota_cost`: Official quota-unit cost, expected to be `50`
- `auth_mode`: Required access mode, expected to be `oauth_required`
- `request_shape`: Maintainer-visible declaration of required and optional request fields
- `notes`: Maintainer-facing guidance for required `channelId`, watermark resource metadata, media-upload constraints, optional partner-only delegation, unsupported request shapes, and failure boundaries

**Validation Rules**:

- Must identify `watermarks.set` consistently across metadata, docs, contracts, and review surfaces
- Must expose quota cost `50` wherever endpoint metadata is reviewed
- Must expose OAuth-required access expectations
- Must identify `channelId`, watermark resource metadata, and `media` upload content as required supported inputs
- Must document that successful execution is represented as a watermark-update acknowledgement rather than a returned watermark resource
- Must document upload MIME type and size boundaries so unsupported media is rejected or clearly flagged before or during execution
- Must document that unsupported modifiers are outside the supported boundary unless explicitly added to the wrapper contract

**Relationships**:

- Defines the contract used by `Watermark Set Request`
- Produces or classifies `Watermark Update Acknowledgement` and `Watermark Failure Outcome`
- Feeds downstream review surfaces and higher-layer summaries without introducing a public MCP tool in this slice

## Watermark Set Request

**Purpose**: Represents one supported request to upload and set a YouTube channel watermark through the internal Layer 1 wrapper.

**Fields**:

- `channelId`: Required target YouTube channel identifier
- `body`: Required watermark resource metadata, including timing, position, and optional target-channel link details when supported by the final wrapper contract
- `media`: Required upload payload containing the watermark image content and MIME type
- `onBehalfOfContentOwner`: Optional partner-only delegated content-owner context if, and only if, the final wrapper contract deliberately supports it

**Validation Rules**:

- `channelId` is required
- `channelId` must be a non-empty string after trimming surrounding whitespace
- `body` is required and must provide the supported watermark resource metadata boundary
- `media` is required and must include supported upload content and MIME type details
- Supported MIME types are expected to remain `image/jpeg`, `image/png`, and `application/octet-stream`
- Media content must remain within the documented maximum upload size of 10 MB
- Requests with blank, missing, malformed, incomplete, or unsupported channel, metadata, or media fields must be rejected or clearly flagged before execution when determinable locally
- Unsupported top-level fields must be rejected or clearly flagged rather than silently forwarded
- Partner-only delegation must either be explicitly supported and documented or clearly flagged as outside the guaranteed boundary
- A valid request still requires OAuth-backed access and may still fail because of ownership, permissions, policy state, media eligibility, channel availability, or upstream conditions

**Relationships**:

- Valid requests are evaluated against `Watermarks Set Wrapper Contract`
- Successful execution produces `Watermark Update Acknowledgement`
- Invalid, unauthorized, unsupported, or refused execution produces `Watermark Failure Outcome`

## Watermark Upload Payload

**Purpose**: Represents the upload-specific part of a `watermarks.set` request.

**Fields**:

- `mimeType`: Media content type, expected to be one of the supported upload MIME types
- `content`: Image content for the watermark upload
- `sizeBytes`: Derived or declared media size used for validation and review

**Validation Rules**:

- Must be present for supported `watermarks.set` requests
- Must not be empty
- Must not exceed 10 MB
- Must use a supported MIME type
- Must not expose raw media bytes in logs, docs, review summaries, or normalized result payloads

**Relationships**:

- Included in `Watermark Set Request`
- May produce `Watermark Failure Outcome` when missing, unsupported, too large, or rejected by upstream image validation

## Watermark Update Acknowledgement

**Purpose**: Represents the normalized success result for an accepted `watermarks.set` request, including enough context for downstream layers to know what was updated without requiring an upstream response body.

**Fields**:

- `is_set` or equivalent acknowledgement flag: Indicates the watermark-set request was accepted as successful
- `channel_id`: Target channel identifier from the accepted request
- `source_operation`: Expected to remain `watermarks.set`
- `source_auth_mode`: Expected to remain `oauth_required`
- `source_quota_cost`: Expected to remain `50`
- `source_required_fields`: Expected to include `channelId`, `body`, and `media`
- `source_notes`: Review guidance from wrapper metadata

**Validation Rules**:

- Must not include OAuth tokens, credentials, secret-backed values, or raw uploaded image bytes
- Must not expose channel owner identity unless a later contract explicitly requires and protects it
- Must remain distinguishable from validation failures, authorization failures, unsupported media outcomes, upstream refusal outcomes, and upstream unavailability
- Must preserve enough target context for downstream layers to identify the acknowledged watermark update

**State Transitions**:

- `requested` -> `acknowledged` when a valid authorized request succeeds
- `requested` -> `failed` when local validation, authorization, media validation, or upstream execution fails

## Watermark Failure Outcome

**Purpose**: Represents one normalized non-success outcome from a `watermarks.set` request so downstream callers can distinguish what kind of remediation is needed.

**Fields**:

- `category`: Failure classification such as `invalid_request`, access-related failure, unsupported media, `forbidden`, or `upstream_unavailable`
- `message`: Maintainer-safe failure description
- `status_code`: Upstream status code when execution reached the upstream service
- `channel_id`: Target channel identifier when safe and available
- `source_operation`: Expected to remain `watermarks.set`

**Validation Rules**:

- Missing or malformed `channelId`, `body`, or `media` must be classified separately from access and upstream failures
- Missing or incompatible OAuth-backed access must be classified separately from malformed input
- Unsupported media type or oversized upload content must remain distinguishable from channel-authorization failures
- Upstream image validation failures must remain distinguishable from local validation failures and missing authorization
- Upstream forbidden channel failures must remain distinguishable from successful watermark acknowledgements
- Transient upstream failures must remain distinguishable from caller-correctable request errors
- Sensitive credentials, tokens, and raw media content must never appear in failure outcomes

**Relationships**:

- Produced from invalid `Watermark Set Request` inputs or from normalized upstream execution failures
- Used by tests and higher-layer summaries to preserve actionable failure boundaries
