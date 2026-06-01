# Data Model: YT-205 Layer 2 Tool `captions_insert`

## Captions Insert Tool

**Purpose**: Represents the public Layer 2 MCP tool that exposes the upstream `captions.insert` endpoint.

**Fields**:

- `tool_name`: Always `captions_insert`
- `upstream_resource`: Always `captions`
- `upstream_method`: Always `insert`
- `operation_key`: Stable identity `captions.insert`
- `quota_cost`: Official quota-unit cost `400`
- `auth_mode`: `oauth_required`
- `availability_state`: Active media-upload operation, with caption access, delegated-owner, and deprecated `sync` caveats visible
- `description`: Caller-facing discovery description that includes upstream identity, quota cost, auth summary, and upload summary
- `input_schema`: Public request schema for `part`, caption metadata body, caption media input, optional delegation context, and optional deprecated `sync` handling if supported
- `handler`: Callable behavior that validates, invokes the Layer 1 wrapper, and maps the result
- `usage_notes`: Caller-facing examples and quota/auth/upload/delegation notes
- `response_boundary`: Near-raw endpoint-backed created caption-resource result

**Validation Rules**:

- Must derive its name from `captions.insert` using the shared `resource_method` naming rule
- Must include quota cost `400` in metadata, description, and examples
- Must expose OAuth-required auth before invocation
- Must expose the media-upload requirement before invocation
- Must not include API keys, OAuth tokens, stack traces, signed URLs, raw media payloads, caption file contents, or secret values in metadata, examples, errors, or logs
- Must remain a single-endpoint Layer 2 tool and must not add transcript download, language ranking, enrichment, translation, or cross-endpoint composition

**Relationships**:

- Owns one `Captions Insert Request`
- Produces one `Created Caption Resource Result` or one `Captions Insert Error Outcome`
- Uses one Layer 1 `captions.insert` wrapper
- References one `Captions Insert Metadata Disclosure`

## Captions Insert Request

**Purpose**: Represents caller input for one `captions_insert` invocation.

**Fields**:

- `part`: Required comma-separated caption resource parts. The official insert path requires `snippet`; `id` may be response-selected where supported by the endpoint contract.
- `body`: Required caption resource metadata body
- `media`: Required caption media descriptor or media input accepted by the public tool contract
- `onBehalfOfContentOwner`: Optional delegated content-owner context for eligible authorized callers
- `sync`: Deprecated optional upstream synchronization flag when supported by the implementation contract

**Validation Rules**:

- Must include `part`
- Must include required caption metadata body fields
- Must include supported caption media input
- Must require eligible OAuth authorization
- Must reject missing OAuth authorization before endpoint execution
- Must reject unsupported fields when the public schema disallows them
- Must validate delegated content-owner context without exposing credential details
- Must treat `sync` as deprecated if it is accepted at all

**Relationships**:

- Uses one `Caption Metadata Body`
- Uses one `Caption Media Input`
- Uses one `OAuth Requirement`
- May include one `Delegation Context`
- May include one `Deprecated Sync Option`
- Is validated before Layer 1 wrapper invocation

## Caption Metadata Body

**Purpose**: Represents the caption resource metadata required to create a caption track.

**Fields**:

- `snippet.videoId`: Required video identifier for the caption track
- `snippet.language`: Required caption language
- `snippet.name`: Required caption track name
- `snippet.isDraft`: Optional draft-state flag

**Validation Rules**:

- Must be present with a `snippet` object
- Must include non-empty `videoId`, `language`, and `name`
- Must keep `snippet.name` within the supported endpoint limits
- Must not include credential details or raw caption file contents
- Must remain metadata for one created caption resource rather than a higher-level transcript workflow

**Relationships**:

- Belongs to one `Captions Insert Request`
- Is preserved as safe operation context when useful
- May produce one `Captions Insert Error Outcome` for missing or invalid metadata

## Caption Media Input

**Purpose**: Represents the uploaded caption track contents and safe media descriptor required for caption creation.

**Fields**:

- `content`: Supported caption content representation or test-safe placeholder accepted by the implementation contract
- `mimeType`: Optional or required media MIME type, depending on the final schema
- `filename`: Optional safe filename or label when useful for diagnostics
- `sizeBytes`: Optional safe size descriptor for validation and review

**Validation Rules**:

- Must be present for every supported creation request
- Must not expose raw caption file contents in public metadata, examples, errors, or logs
- Must respect the documented maximum file size and accepted MIME type caveats when those are enforced locally
- Must be represented safely in tests without real private caption content
- Must not trigger caption download or transcript extraction

**Relationships**:

- Belongs to one `Captions Insert Request`
- Affects the created caption resource
- May produce one `Captions Insert Error Outcome` for missing or unsupported media input

## OAuth Requirement

**Purpose**: Describes the credential expectation for caption creation before invocation.

**Fields**:

- `auth_mode`: Always `oauth_required`
- `scope_note`: Caller-facing explanation that caption insertion requires eligible YouTube OAuth authorization
- `safe_error_category`: Shared error category when eligible authorization is missing or insufficient

**Validation Rules**:

- Must not present `captions_insert` as API-key-compatible
- Must not expose credential values, token names, or secret configuration details
- Must map missing eligible authorization to a stable caller-facing auth error
- Must distinguish insufficient upload permission from invalid metadata or missing media input

**Relationships**:

- Applies to every `Captions Insert Request`
- Appears in `Captions Insert Metadata Disclosure`
- May produce one `Captions Insert Error Outcome`

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

- May belong to one `Captions Insert Request`
- May appear as safe context in one `Created Caption Resource Result`
- May produce one `Captions Insert Error Outcome` if authorization is missing or insufficient

## Deprecated Sync Option

**Purpose**: Represents the official but deprecated `sync` parameter when the public contract chooses to expose it.

**Fields**:

- `sync`: Optional boolean flag
- `deprecation_note`: Caller-facing warning that the option is deprecated and not the recommended path

**Validation Rules**:

- Must not be required
- Must not be shown as the primary example
- Must be clearly marked deprecated wherever accepted
- Must not add higher-level transcript alignment semantics beyond the upstream parameter

**Relationships**:

- May belong to one `Captions Insert Request`
- Appears in `Captions Insert Metadata Disclosure` as a caveat

## Created Caption Resource Result

**Purpose**: Represents a successful near-raw caption resource response from `captions_insert`.

**Fields**:

- `item`: Returned caption resource or equivalent created-resource payload
- `requestedParts`: Parts requested by the caller
- `endpoint`: Upstream identity `captions.insert`
- `quotaCost`: Official quota-unit cost `400`
- `metadata`: Safe summary of required caption metadata
- `media`: Safe summary of supplied media descriptor, excluding raw content
- `delegation`: Safe indication of whether delegation context was supplied when useful

**Validation Rules**:

- Must preserve returned caption-resource fields from the endpoint-backed response
- Must preserve requested parts for review/debugging
- Must not fabricate missing upstream fields
- Must not include raw caption media content, credentials, or signed URLs
- Must not add higher-level language ranking, transcript lookup, enrichment, translation, or heuristic interpretation

**Relationships**:

- Produced by one valid `Captions Insert Request`
- References one `Captions Insert Metadata Disclosure`

## Captions Insert Error Outcome

**Purpose**: Represents a safe caller-facing failure for invalid requests, auth failures, quota failures, inaccessible videos, duplicate caption conflicts, unavailable upstream service, or unexpected upstream failures.

**Fields**:

- `category`: Shared safe error category
- `message`: Caller-facing remediation-oriented message
- `details`: Safe request context such as tool name, invalid field, metadata presence, media presence, delegation presence, or upstream operation

**Validation Rules**:

- Must not include stack traces, API keys, OAuth tokens, secret values, signed URLs, raw media payloads, caption file contents, or sensitive owner credential details
- Must distinguish invalid metadata from missing media input
- Must distinguish missing authorization from insufficient upload permission
- Must preserve shared Layer 2 error categories where applicable

**Relationships**:

- Produced by one invalid or failed `Captions Insert Request`
- Uses shared YT-201/YT-202 error and safety conventions

## Captions Insert Metadata Disclosure

**Purpose**: Captures the pre-invocation metadata clients and reviewers need to understand the tool.

**Fields**:

- `name`: `captions_insert`
- `upstream`: `captions.insert`
- `quotaCost`: `400`
- `authMode`: `oauth_required`
- `availabilityState`: Active media-upload operation with caption-access, delegation, and deprecated-option caveats
- `inputContract`: Required `part`, required caption metadata body, required media input, optional delegation context, and deprecated `sync` caveat where supported
- `responseBoundary`: Near-raw created caption-resource response with light MCP clarity fields
- `usageNotes`: Examples for authorized caption creation, delegated content-owner context, metadata-only validation failure, media-only validation failure, and authorization-sensitive failure

**Validation Rules**:

- Must be visible before invocation
- Must include quota, auth, and media-upload details in both structured metadata and caller-facing text
- Must describe delegated content-owner context
- Must describe deprecated `sync` behavior if the parameter is accepted
- Must stay aligned with YT-201/YT-202 shared metadata standards

**Relationships**:

- Belongs to the `Captions Insert Tool`
- References `Captions Insert Request`, `Caption Metadata Body`, `Caption Media Input`, `OAuth Requirement`, `Delegation Context`, `Deprecated Sync Option`, and `Created Caption Resource Result`

## Verification Evidence

**Purpose**: Captures proof that the endpoint tool is ready for implementation review.

**Fields**:

- `red_phase_evidence`: Failing or characterization tests added before implementation
- `discovery_contract_checks`: Checks that `captions_insert` appears with required metadata
- `request_validation_checks`: Checks for required `part`, metadata, media input, delegation, deprecated option, and unsupported-field rules
- `auth_checks`: Checks for OAuth-required behavior and delegated-owner guidance
- `result_checks`: Checks for created caption resource, requested parts, safe media summary, and operation context preservation
- `error_checks`: Checks for safe error categories and sanitized details
- `full_suite_command`: `python3 -m pytest`
- `lint_command`: `python3 -m ruff check .`
- `docstring_review`: Confirmation that changed Python functions include reStructuredText docstrings

**Validation Rules**:

- Must include Red-Green-Refactor evidence
- Must include focused checks before full-suite validation
- Must include full repository validation after final code changes
- Must include lint validation after final code changes
- Must identify any official documentation caveats discovered during implementation
