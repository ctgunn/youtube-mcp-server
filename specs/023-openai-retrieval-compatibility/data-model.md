# Data Model: OpenAI Retrieval Compatibility

## Overview

FND-023 does not introduce persistent storage. The design work centers on the external retrieval contract and the runtime entities that must stay aligned across discovery metadata, tool invocation, result shaping, and hosted verification.

## Entities

### 1. OpenAI Search Request

- **Purpose**: Represents the supported OpenAI-compatible input to the `search` tool.
- **Fields**:
  - `query`
    - Type: string
    - Required: yes
    - Validation: non-empty, user-provided query string
- **Validation rules**:
  - Must be accepted from discovery output alone.
  - Must reject unsupported extra fields unless they are part of a documented compatibility path.
- **Relationships**:
  - Produces zero or more `OpenAI Search Result` records.

### 2. OpenAI Search Result

- **Purpose**: Represents one search hit returned by `search` in the OpenAI-compatible result shape.
- **Fields**:
  - `id`
    - Type: string
    - Required: yes
    - Meaning: stable identifier for follow-up retrieval
  - `title`
    - Type: string
    - Required: yes
    - Meaning: human-readable result title
  - `url`
    - Type: string
    - Required: yes
    - Meaning: canonical citation URL
- **Validation rules**:
  - Every result must include all three fields.
  - Results may be empty as a successful non-error outcome.
- **Relationships**:
  - `id` is the valid lookup key for `OpenAI Fetch Request`.

### 3. OpenAI Fetch Request

- **Purpose**: Represents the supported OpenAI-compatible input to the `fetch` tool.
- **Fields**:
  - `id`
    - Type: string
    - Required: yes
    - Meaning: unique identifier for the selected search document or result
- **Validation rules**:
  - Must accept a single identifier argument that matches a previously published or otherwise valid document identifier.
  - Unsupported legacy identifier shapes must adapt through a documented boundary or fail predictably.
- **Relationships**:
  - Resolves to one `OpenAI Fetch Result` or one structured retrieval failure.

### 4. OpenAI Fetch Result

- **Purpose**: Represents the content returned by `fetch` in the OpenAI-compatible shape.
- **Fields**:
  - `id`
    - Type: string
    - Required: yes
    - Meaning: unique identifier for the retrieved document
  - `title`
    - Type: string
    - Required: yes
    - Meaning: title of the retrieved result
  - `text`
    - Type: string
    - Required: yes
    - Meaning: full retrieved text content
  - `url`
    - Type: string
    - Required: yes
    - Meaning: canonical result URL
  - `metadata`
    - Type: object
    - Required: no
    - Meaning: optional key/value context about the result
- **Validation rules**:
  - Success responses must include the required fields in both text-encoded and structured forms.
  - Optional metadata must be safe for hosted exposure.
- **Relationships**:
  - Returned by `fetch` for a valid `OpenAI Fetch Request`.

### 5. Compatibility Boundary

- **Purpose**: Defines how the service distinguishes the supported OpenAI retrieval contract from older repo-specific retrieval shapes.
- **Fields**:
  - `supported_contract`
    - Type: enum-like descriptive value
    - Meaning: the OpenAI-compatible `search`/`fetch` shape supported by FND-023
  - `legacy_shape_policy`
    - Type: descriptive value
    - Meaning: whether legacy shapes are adapted explicitly or rejected explicitly
  - `failure_outcome`
    - Type: structured error category
    - Meaning: stable failure behavior for unsupported shapes
- **Validation rules**:
  - Must be documented in discovery, contracts, or quickstart guidance closely enough for maintainers and operators to understand the behavior.

### 6. Compatibility Verification Record

- **Purpose**: Captures the evidence that the OpenAI-compatible retrieval flow works through protected MCP access.
- **Fields**:
  - `check_name`
    - Type: string
    - Required: yes
  - `flow_stage`
    - Type: string
    - Required: yes
    - Examples: initialize, tools-list, search-call, fetch-call, legacy-shape-failure
  - `result`
    - Type: success/fail outcome
    - Required: yes
  - `evidence`
    - Type: descriptive payload or reference
    - Required: yes
  - `failure_category`
    - Type: optional string
    - Required: no
- **Validation rules**:
  - Must distinguish success for OpenAI-compatible retrieval calls from failures caused by unsupported legacy request shapes.
  - Must remain safe for hosted logs and artifacts.

## Relationships Summary

- One `OpenAI Search Request` yields zero or more `OpenAI Search Result` records.
- One `OpenAI Search Result.id` can become one `OpenAI Fetch Request.id`.
- One `OpenAI Fetch Request` yields one `OpenAI Fetch Result` or one structured failure.
- One `Compatibility Boundary` governs how the service handles legacy request shapes during or after alignment.
- One `Compatibility Verification Record` proves each expected discovery, search, fetch, and failure-path behavior.

## State Transitions

### Search Flow

1. Client discovers `search`.
2. Client sends `OpenAI Search Request`.
3. Service returns either:
   - successful `results` array, or
   - successful empty `results` array, or
   - structured invalid-request failure.

### Fetch Flow

1. Client discovers `fetch`.
2. Client sends `OpenAI Fetch Request`.
3. Service returns either:
   - successful `OpenAI Fetch Result`, or
   - structured unavailable-result failure, or
   - structured unsupported-shape failure.

### Legacy Shape Transition

1. Client sends a request using the older repo-specific shape.
2. Service either:
   - adapts it through the documented compatibility boundary, or
   - rejects it with a stable structured failure that identifies the supported contract boundary.
