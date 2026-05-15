# Data Model: YT-152 Layer 1 Endpoint `videos.reportAbuse`

## Entity: Videos Report Abuse Wrapper Contract

**Purpose**: Describes the internal Layer 1 wrapper for `videos.reportAbuse` in a way that exposes endpoint identity, quota cost, supported report-body boundaries, authorization expectations, and normalized mutation acknowledgement rules before implementation details are inspected.

**Fields**:

- `resource_name`: Upstream resource name, expected to remain `videos`
- `operation_name`: Upstream operation name, expected to remain `reportAbuse`
- `operation_key`: Stable combined identifier used in tests and review surfaces
- `http_method`: Upstream HTTP method for the wrapper
- `path_shape`: Upstream path or route pattern for the wrapper
- `request_shape`: Allowed request fields for the wrapper contract
- `auth_mode`: Stable auth mode for this endpoint, expected to remain OAuth-required
- `quota_cost`: Official quota-unit cost of `50`
- `notes`: Maintainer-facing notes for required report body fields, optional payload fields, unsupported partner-only query behavior, and normalized acknowledgement interpretation

**Validation Rules**:

- `resource_name`, `operation_name`, `http_method`, `path_shape`, `request_shape`, `auth_mode`, and `quota_cost` are required
- `quota_cost` must equal the official endpoint cost captured for this slice
- `auth_mode` must remain reviewable as OAuth-required rather than hiding access expectations in runtime-only behavior
- The wrapper contract is incomplete if required payload guidance or successful acknowledgement notes are not visible in maintainer-facing artifacts

**Relationships**:

- Uses one `Video Abuse Report Request`
- Produces one `Video Abuse Report Outcome`
- Shares failure categories with `Report Failure Outcome`
- Is exercised through the shared executor and representative wrapper flow under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`

## Entity: Video Abuse Report Request

**Purpose**: Represents one supported `videos.reportAbuse` request shape that identifies the video being reported, the primary abuse reason, and any supported optional report details.

**Fields**:

- `body`: Required report payload object
- `body.videoId`: Required identifier of the video being reported
- `body.reasonId`: Required abuse-report reason identifier
- `body.secondaryReasonId`: Optional secondary abuse-report reason identifier
- `body.comments`: Optional reporter-supplied explanatory text
- `body.language`: Optional language indicator for reporter-supplied detail
- `unsupported_fields_policy`: Explicit statement that undocumented request fields and partner-only query parameters are outside this feature's promised contract
- `request_mode`: Maintainer-facing label that distinguishes a valid report request from unsupported incomplete shapes

**Validation Rules**:

- A supported report request must include `body`
- `body.videoId` and `body.reasonId` are required and must be non-empty
- `body.secondaryReasonId`, `body.comments`, and `body.language` are the only supported optional body fields for this slice
- Partner-only `onBehalfOfContentOwner` behavior is outside the guaranteed boundary for this slice and must be rejected or clearly flagged if submitted
- Unsupported or unexpected top-level fields and body fields must be rejected or clearly flagged before execution
- The request contract must remain deterministic and must not silently rewrite incomplete or broader report input into supported behavior

**Relationships**:

- Belongs to one `Videos Report Abuse Wrapper Contract`
- Produces one `Video Abuse Report Outcome` or one `Report Failure Outcome`
- May reference reason identifiers discovered separately through `videoAbuseReportReasons.list`

## Entity: Abuse Report Payload Guidance

**Purpose**: Describes the reviewable payload rules maintainers need before composing or validating abuse-report requests.

**Fields**:

- `required_body_fields`: `videoId` and `reasonId`
- `optional_body_fields`: `secondaryReasonId`, `comments`, and `language`
- `reason_source_note`: Explanation that reason identifiers are expected to align with the platform's abuse-report reason inventory
- `secondary_reason_note`: Explanation that a secondary reason is only valid when it forms an accepted combination with the primary reason
- `partner_delegation_boundary`: Statement that delegated content-owner query behavior is outside the guaranteed contract for this slice
- `sensitive_data_note`: Statement that credentials, tokens, and reporter identity must not be exposed in docs, logs, or normalized outcomes

**Validation Rules**:

- Required and optional fields must remain visible in wrapper metadata, feature-local contracts, and implementation docstrings
- The guidance must distinguish invalid or unsupported local payloads from upstream refusals for otherwise validly shaped reports
- The guidance must avoid embedding credential values or report submitter identity

**Relationships**:

- Applies to one `Videos Report Abuse Wrapper Contract`
- Governs `Video Abuse Report Request` validation and review surfaces

## Entity: Video Abuse Report Outcome

**Purpose**: Represents the normalized successful acknowledgement of a valid `videos.reportAbuse` request.

**Fields**:

- `isAccepted`: Boolean-style acknowledgement that the report submission succeeded
- `reportedVideoId`: Stable echo of the submitted target video identifier
- `reasonId`: Stable echo of the submitted primary abuse reason
- `secondaryReasonId`: Optional echo of the submitted secondary abuse reason, when present
- `hasComments`: Boolean-style indicator that optional explanatory comments were submitted without exposing the comment text unnecessarily in summaries
- `language`: Optional echo of the submitted language indicator, when present
- `sourceOperation`: Stable source-operation identifier preserved for review and downstream mapping
- `authPath`: Maintainer-facing label showing the OAuth-required path used by this wrapper
- `metadata_visibility`: Whether quota, auth, and payload guidance remain attached to the wrapper rather than being lost in the result payload

**Validation Rules**:

- A valid report request must end as either a successful acknowledgement or a normalized upstream failure
- Successful acknowledgement results must preserve enough context to identify which video and reason were submitted
- Successful acknowledgement results must not expose OAuth tokens, credentials, or report submitter identity
- Optional comment text should not be echoed in higher-layer summaries unless a later requirement explicitly needs it

**Relationships**:

- Returned by one `Videos Report Abuse Wrapper Contract`
- Derived from one `Video Abuse Report Request`

## Entity: Report Failure Outcome

**Purpose**: Represents one normalized non-success outcome from a `videos.reportAbuse` request so downstream callers can distinguish what kind of remediation is needed.

**Fields**:

- `category`: Stable failure category such as invalid request, access-related failure, upstream refusal, rate-limit failure, video-not-found, or upstream unavailable
- `reason`: Maintainer-visible explanation of what failed
- `request_mode`: The abuse-report request mode that triggered the failure, when known
- `source_operation`: Stable endpoint identifier preserved for diagnostics
- `retryability`: Whether the failure suggests caller correction, access correction, rate-limit handling, or upstream-side retry
- `upstream_category_examples`: Representative normalized categories such as `invalid_request`, `auth`, `forbidden`, `rate_limited`, `not_found`, and `upstream_unavailable`

**Validation Rules**:

- Local validation failures must remain distinct from access failures
- Access failures must remain distinct from upstream report refusals after execution begins
- Invalid abuse-reason combinations returned by the upstream service must remain distinguishable from locally missing `reasonId`
- Video-not-found and rate-limit outcomes must remain distinguishable enough for downstream remediation
- Successful report acknowledgements must not be represented through this failure entity

**Relationships**:

- May be produced instead of one `Video Abuse Report Outcome`
- Shares wrapper metadata and request context with the `Videos Report Abuse Wrapper Contract`

## State Transitions

### Wrapper Review Lifecycle

1. `draft`: Endpoint metadata exists but payload-boundary or acknowledgement guidance may still be implicit
2. `reviewable`: Endpoint identity, quota cost, OAuth requirement, required body fields, optional body fields, and 204 acknowledgement semantics are visible together
3. `validated`: Unit, contract, integration, and transport checks prove body validation, OAuth-only guidance, normalized acknowledgement handling, and failure-boundary behavior
4. `reusable`: Later abuse-reporting work can consume the wrapper contract without extra endpoint research

### Request Outcome Lifecycle

1. Caller supplies one supported abuse-report request shape
2. Wrapper validates required body object, required body fields, optional body field boundary, and unsupported top-level field rejection
3. OAuth eligibility is evaluated before execution
4. Shared executor runs with authorized access for the validated report request
5. Request ends as either `successful report acknowledgement`, `normalized invalid_request`, `normalized auth failure`, `normalized forbidden/refusal`, `normalized rate_limited`, `normalized video_not_found`, or `normalized upstream_unavailable`
