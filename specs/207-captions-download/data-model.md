# Data Model: YT-207 Layer 2 Tool `captions_download`

## Captions Download Tool

**Purpose**: Represents the public Layer 2 MCP tool that exposes the upstream `captions.download` endpoint.

**Fields**:

- `tool_name`: Always `captions_download`
- `upstream_resource`: Always `captions`
- `upstream_method`: Always `download`
- `operation_key`: Stable identity `captions.download`
- `quota_cost`: Official quota-unit cost `200`
- `auth_mode`: `oauth_required`
- `availability_state`: Active permission-sensitive download operation, with caption access, delegated-owner, and conversion caveats visible
- `description`: Caller-facing discovery description that includes upstream identity, quota cost, auth summary, permission summary, identifier requirement, and conversion summary
- `input_schema`: Public request schema for required caption track `id`, optional `tfmt`, optional `tlang`, and optional delegation context
- `handler`: Callable behavior that validates, invokes the Layer 1 wrapper, and maps the result
- `usage_notes`: Caller-facing examples and quota/auth/permission/format/language/delegation notes
- `response_boundary`: Near-raw endpoint-backed downloaded-content result

**Validation Rules**:

- Must derive its name from `captions.download` using the shared `resource_method` naming rule
- Must include quota cost `200` in metadata, description, and examples
- Must expose OAuth-required auth before invocation
- Must expose the permission-to-edit caveat before invocation
- Must expose required caption track `id` before invocation
- Must expose supported format and language conversion options before invocation
- Must not include API keys, OAuth tokens, stack traces, signed URLs, raw private caption content, binary payloads, or secret values in metadata, examples, errors, or logs
- Must remain a single-endpoint Layer 2 tool and must not add caption listing, caption creation, caption update, caption deletion, transcript summarization, language ranking, enrichment, translation beyond upstream `tlang`, or cross-endpoint composition

**Relationships**:

- Owns one `Caption Download Request`
- Produces one `Downloaded Caption Content Result` or one `Captions Download Error Outcome`
- Uses one Layer 1 `captions.download` wrapper
- References one `Captions Download Metadata Disclosure`

## Caption Download Request

**Purpose**: Represents caller input for one `captions_download` invocation.

**Fields**:

- `id`: Required caption track identifier.
- `tfmt`: Optional output format value. Supported values are `sbv`, `scc`, `srt`, `ttml`, and `vtt`.
- `tlang`: Optional target language value represented as an ISO 639-1 two-letter language code.
- `onBehalfOfContentOwner`: Optional delegated content-owner context for eligible authorized callers.

**Validation Rules**:

- Must include non-empty `id`
- Must require eligible OAuth authorization
- Must reject missing OAuth authorization before endpoint execution
- Must reject unsupported `tfmt` values
- Must reject malformed `tlang` values
- Must validate delegated content-owner context without exposing credential details
- Must reject unsupported fields when the public schema disallows them
- Must not include a request body

**Relationships**:

- Uses one `Caption Track Identifier`
- May use one `Output Format Option`
- May use one `Target Language Option`
- Uses one `Permission Requirement`
- May include one `Delegation Context`
- Is validated before Layer 1 wrapper invocation

## Caption Track Identifier

**Purpose**: Identifies the specific caption track whose content should be downloaded.

**Fields**:

- `id`: Non-empty caption track identifier as represented by a caption resource.

**Validation Rules**:

- Must be present for every request
- Must be non-empty
- Must not be replaced by video id, language, caption name, or inferred lookup state
- Must not expose private video-owner details beyond the safe identifier supplied by the caller

**Relationships**:

- Belongs to one `Caption Download Request`
- Appears in safe operation context when useful
- May produce one `Captions Download Error Outcome` for missing, invalid, inaccessible, or not-found caption tracks

## Output Format Option

**Purpose**: Represents an optional requested caption output format for the downloaded file.

**Fields**:

- `tfmt`: One of `sbv`, `scc`, `srt`, `ttml`, or `vtt`
- `format_note`: Caller-facing explanation that omitting `tfmt` returns the original format when upstream supports it

**Validation Rules**:

- Must be optional
- Must be one of the documented supported values when supplied
- Must not trigger local transcript parsing or formatting outside the upstream endpoint behavior
- Must be preserved as safe operation context when useful

**Relationships**:

- May belong to one `Caption Download Request`
- May affect one `Downloaded Caption Content Result`
- May produce one `Captions Download Error Outcome` when unsupported or when upstream cannot convert the caption track

## Target Language Option

**Purpose**: Represents an optional requested target language conversion for the downloaded caption content.

**Fields**:

- `tlang`: ISO 639-1 two-letter target language code
- `translation_note`: Caller-facing explanation that upstream translation is machine-generated when the option is accepted

**Validation Rules**:

- Must be optional
- Must use a two-letter language-code shape when supplied
- Must not accept arbitrary prose language names
- Must not imply local translation or local language ranking
- Must be preserved as safe operation context when useful

**Relationships**:

- May belong to one `Caption Download Request`
- May affect one `Downloaded Caption Content Result`
- May produce one `Captions Download Error Outcome` when malformed or when upstream cannot convert the caption track

## Permission Requirement

**Purpose**: Describes the credential and access expectation for caption download before invocation.

**Fields**:

- `auth_mode`: Always `oauth_required`
- `permission_note`: Caller-facing explanation that caption download requires eligible YouTube OAuth authorization and permission to edit the video
- `safe_error_category`: Shared error category when eligible authorization is missing or insufficient

**Validation Rules**:

- Must not present `captions_download` as API-key-compatible
- Must not expose credential values, token names, or secret configuration details
- Must map missing eligible authorization to a stable caller-facing auth error
- Must distinguish insufficient download permission from invalid request shape or missing caption resource

**Relationships**:

- Applies to every `Caption Download Request`
- Appears in `Captions Download Metadata Disclosure`
- May produce one `Captions Download Error Outcome`

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

- May belong to one `Caption Download Request`
- May appear as safe context in one `Downloaded Caption Content Result`
- May produce one `Captions Download Error Outcome` if authorization is missing or insufficient

## Downloaded Caption Content Result

**Purpose**: Represents a successful near-raw caption-content response from `captions_download`.

**Fields**:

- `content`: Downloaded caption content or safe content representation accepted by the MCP result contract
- `contentType`: Response content type when available, expected to reflect the upstream binary-file response context
- `contentForm`: Indicator that distinguishes text, binary, encoded, or descriptor-shaped content representation
- `sizeBytes`: Optional safe size descriptor when available
- `requestedFormat`: Requested `tfmt` value when supplied
- `requestedLanguage`: Requested `tlang` value when supplied
- `endpoint`: Upstream identity `captions.download`
- `quotaCost`: Official quota-unit cost `200`
- `download`: Safe summary of the caption track identity and conversion options
- `delegation`: Safe indication of whether delegation context was supplied when useful

**Validation Rules**:

- Must preserve downloaded caption content or the supported safe content representation
- Must preserve requested conversion options for review/debugging
- Must not fabricate transcript segments, summaries, rankings, or language metadata
- Must not include API keys, OAuth tokens, signed URLs, or secret values
- Must not expose raw private caption content in public examples, logs, or errors
- Must not add higher-level caption listing, caption creation, caption update, caption deletion, enrichment, or heuristic interpretation

**Relationships**:

- Produced by one valid `Caption Download Request`
- References one `Captions Download Metadata Disclosure`

## Captions Download Error Outcome

**Purpose**: Represents a safe caller-facing failure for invalid requests, auth failures, quota failures, missing caption tracks, insufficient permissions, conversion failures, unavailable upstream service, or unexpected upstream failures.

**Fields**:

- `category`: Shared safe error category
- `message`: Caller-facing remediation-oriented message
- `details`: Safe request context such as tool name, invalid field, caption track id presence, requested format, requested language, delegation presence, or upstream operation

**Validation Rules**:

- Must not include stack traces, API keys, OAuth tokens, secret values, signed URLs, raw private caption content, binary payloads, or sensitive owner credential details
- Must distinguish invalid identifier from unsupported conversion input
- Must distinguish missing authorization from insufficient download permission
- Must distinguish missing caption tracks from invalid request shape
- Must distinguish conversion failure from successful empty content
- Must preserve shared Layer 2 error categories where applicable

**Relationships**:

- Produced by one invalid or failed `Caption Download Request`
- Uses shared YT-201/YT-202 error and safety conventions

## Captions Download Metadata Disclosure

**Purpose**: Captures the pre-invocation metadata clients and reviewers need to understand the tool.

**Fields**:

- `name`: `captions_download`
- `upstream`: `captions.download`
- `quotaCost`: `200`
- `authMode`: `oauth_required`
- `availabilityState`: Active permission-sensitive download operation with caption-access, delegation, and conversion caveats
- `inputContract`: Required `id`, optional `tfmt`, optional `tlang`, optional delegation context, and no request body
- `responseBoundary`: Near-raw downloaded-content response with light MCP clarity fields
- `usageNotes`: Examples for authorized default download, authorized format-specific download, authorized target-language conversion, delegated content-owner context, missing-identifier validation failure, unsupported conversion validation failure, and authorization-sensitive failure

**Validation Rules**:

- Must be visible before invocation
- Must include quota, auth, permission, identifier, format, and language details in both structured metadata and caller-facing text
- Must describe delegated content-owner context
- Must explain downloaded-content response form
- Must stay free of credentials, stack traces, signed URLs, raw private caption content, binary payloads, and secret values

**Relationships**:

- Describes one `Captions Download Tool`
- Informs validation for every `Caption Download Request`
- Informs review of every `Downloaded Caption Content Result` and `Captions Download Error Outcome`
