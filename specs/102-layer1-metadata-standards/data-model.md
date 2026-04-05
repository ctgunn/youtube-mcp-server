# Data Model: YT-102 Layer 1 Endpoint Metadata, Quota, and Signature Standards

## Entity: Layer 1 Wrapper Metadata Record

**Purpose**: Describes one internal wrapper around an upstream YouTube endpoint in a way that is reviewable before execution.

**Fields**:

- `resource_name`: Upstream resource name used for stable wrapper identity
- `operation_name`: Upstream operation name used for stable wrapper identity
- `operation_key`: Combined resource and operation identifier used in planning and review
- `http_method`: Upstream HTTP method exposed for maintainer review
- `path_shape`: Upstream path or route pattern exposed for maintainer review
- `request_shape`: Required and optional request fields supported by the wrapper
- `auth_mode`: One of `api_key`, `oauth_required`, or `mixed/conditional`
- `quota_cost`: Official quota-unit cost recorded for maintainer review
- `lifecycle_state`: Wrapper lifecycle note such as active, deprecated, limited, or inconsistent-docs
- `caveat_note`: Maintainer-facing explanation of lifecycle, availability, or documentation caveats
- `auth_condition_note`: Maintainer-facing explanation when auth expectations vary by request or caller context

**Validation Rules**:

- `resource_name`, `operation_name`, `http_method`, `path_shape`, `auth_mode`, and `quota_cost` are required
- `quota_cost` must be greater than zero
- `auth_mode` must be one of the supported wrapper-contract values
- `auth_condition_note` is required whenever `auth_mode` is mixed or conditional
- `caveat_note` is required whenever `lifecycle_state` indicates deprecation, limited availability, or documented inconsistency
- The record is incomplete if any required review field is missing from maintainer-visible artifacts

**Relationships**:

- Uses one `Wrapper Request Shape`
- Emits one stable `operation_key` used by reviewers and future higher-layer planning
- Is referenced by one or more `Reviewability Artifacts`
- Implemented primarily in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`

## Entity: Wrapper Request Shape

**Purpose**: Describes the allowed input arguments for one wrapper and anchors the metadata record to a real request contract.

**Fields**:

- `required_fields`: Request fields that must be present
- `optional_fields`: Request fields that may be present

**Validation Rules**:

- At least one required field must exist
- Unexpected request fields are rejected
- Empty strings for required text fields are invalid

**Relationships**:

- Belongs to one `Layer 1 Wrapper Metadata Record`
- Is validated before wrapper execution in the representative wrapper flow

## Entity: Reviewability Artifact

**Purpose**: Any maintainer-facing surface that makes wrapper identity, quota cost, auth expectations, and caveats visible without external research.

**Fields**:

- `artifact_type`: Docstring, signature-adjacent comment, contract markdown, or test evidence
- `wrapper_identity_fields`: The identity details exposed by the artifact
- `quota_visibility`: The quota reference shown in the artifact
- `auth_visibility`: The auth expectation or conditional-auth explanation shown in the artifact
- `caveat_visibility`: The lifecycle or documentation caveat shown in the artifact

**Validation Rules**:

- Every representative wrapper in scope must map to at least one artifact that exposes identity, quota, and auth expectations
- Wrappers with lifecycle caveats must map to at least one artifact that exposes that caveat explicitly
- Artifacts must not expose secrets or runtime credential values

**Relationships**:

- References one or more `Layer 1 Wrapper Metadata Records`
- Supports `Higher-Layer Planning Consumers`
- Proven by contract and integration tests in scope

## Entity: Higher-Layer Planning Consumer

**Purpose**: Represents a maintainer or future Layer 2 or Layer 3 author who evaluates wrappers before composing a new workflow.

**Fields**:

- `consumer_goal`: The planning or review task being performed
- `candidate_wrappers`: The representative wrappers under comparison
- `decision_inputs`: Identity, quota cost, auth expectations, and caveats
- `comparison_outcome`: The conclusion reached about wrapper suitability

**Validation Rules**:

- Consumers must be able to compare representative wrappers using maintainer-visible artifacts rather than raw upstream documentation
- Conditional auth and caveat details must be understandable before implementation starts

**Relationships**:

- Reads from `Reviewability Artifacts`
- Compares one or more `Layer 1 Wrapper Metadata Records`

## State Transitions

### Wrapper Metadata Review Lifecycle

1. `draft`: Wrapper metadata exists but may be missing one or more review fields
2. `reviewable`: Identity, HTTP semantics, quota, auth expectation, and required caveat notes are present and visible
3. `validated`: Unit, contract, and integration checks prove the metadata standard holds for representative wrappers
4. `reusable`: Future Layer 2 or Layer 3 planning can rely on the representative wrapper metadata without extra upstream research

### Caveat Handling Lifecycle

1. Upstream endpoint caveat is discovered
2. Wrapper metadata records lifecycle state and caveat note
3. Reviewability artifacts expose the caveat in maintainer-facing form
4. Tests protect the caveat from being removed or reduced to an implicit note
