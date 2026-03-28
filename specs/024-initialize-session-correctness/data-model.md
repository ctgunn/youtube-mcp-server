# Data Model: Initialize Session Correctness

## Overview

FND-024 does not introduce persistent storage. The design work centers on the runtime entities and lifecycle decisions that determine whether hosted continuation state may begin after an initialize request.

## Entities

### 1. Initialize Request

- **Purpose**: Represents the first hosted MCP handshake request that may establish continuation state.
- **Fields**:
  - `request_id`
    - Type: string or null
    - Required: no
    - Meaning: client-visible request identifier when supplied
  - `method`
    - Type: string
    - Required: yes
    - Meaning: expected to be `initialize`
  - `params`
    - Type: object
    - Required: yes
    - Meaning: initialize parameters including `clientInfo`
  - `security_context`
    - Type: descriptive object
    - Required: yes
    - Meaning: authentication, origin, and hosted request context applied before initialize is accepted
  - `protocol_version`
    - Type: string
    - Required: yes
    - Meaning: requested or default MCP protocol version for the initialize attempt
- **Validation rules**:
  - The request must pass hosted security, JSON parsing, protocol-version checks, and initialize parameter validation before session creation is eligible.
  - A request using method `initialize` but failing any required check is still an initialize attempt, but not a successful initialize outcome.
- **Relationships**:
  - Produces exactly one `Initialize Outcome`.

### 2. Initialize Outcome

- **Purpose**: Represents the accepted or rejected result of an initialize attempt and decides whether continuation state may be issued.
- **Fields**:
  - `status`
    - Type: enum-like descriptive value
    - Required: yes
    - Allowed values: `accepted`, `rejected`
  - `failure_category`
    - Type: string
    - Required: no
    - Meaning: stable failure category when initialize is rejected
  - `protocol_result_present`
    - Type: boolean
    - Required: yes
    - Meaning: whether the hosted response includes a successful initialize result payload
  - `session_creation_allowed`
    - Type: boolean
    - Required: yes
    - Meaning: whether a hosted session may be created and exposed
- **Validation rules**:
  - `session_creation_allowed` may be true only when `status` is `accepted`.
  - Rejected outcomes must not issue a continuation session identifier.
- **Relationships**:
  - Governs whether one `Hosted Session` and one `Continuation Session Identifier` may be created.

### 3. Hosted Session

- **Purpose**: Represents the reusable hosted server-side session context used for follow-up POST and GET continuation.
- **Fields**:
  - `session_id`
    - Type: string
    - Required: yes
  - `protocol_version`
    - Type: string
    - Required: yes
  - `created_at`
    - Type: timestamp string
    - Required: yes
  - `last_activity_at`
    - Type: timestamp string
    - Required: yes
  - `expires_at`
    - Type: timestamp string
    - Required: yes
  - `state`
    - Type: enum-like descriptive value
    - Required: yes
    - Allowed values: `active`, `expired`, `closed`
  - `client_metadata`
    - Type: object or null
    - Required: no
- **Validation rules**:
  - A hosted session may exist only after an accepted initialize outcome.
  - A hosted session created by successful initialize must be usable for follow-up continuation within the documented continuity rules.
- **Relationships**:
  - Is created from one accepted `Initialize Outcome`.
  - Is referenced by one `Continuation Session Identifier`.

### 4. Continuation Session Identifier

- **Purpose**: Represents the client-visible `MCP-Session-Id` header value returned after successful initialize and reused for continuation.
- **Fields**:
  - `header_name`
    - Type: string
    - Required: yes
    - Fixed value: `MCP-Session-Id`
  - `session_id`
    - Type: string
    - Required: yes
  - `issued_on_initialize`
    - Type: boolean
    - Required: yes
  - `issued_once_for_attempt`
    - Type: boolean
    - Required: yes
- **Validation rules**:
  - Must be absent from rejected initialize responses.
  - Must refer to a real `Hosted Session` created by the same accepted initialize attempt.
- **Relationships**:
  - Maps one-to-one to a valid `Hosted Session` for the accepted initialize attempt.

### 5. Continuation Attempt

- **Purpose**: Represents a follow-up GET or POST request that tries to use an existing hosted session.
- **Fields**:
  - `session_id`
    - Type: string
    - Required: yes
  - `request_method`
    - Type: string
    - Required: yes
    - Allowed values: `GET`, `POST`
  - `lifecycle_status`
    - Type: descriptive value
    - Required: yes
    - Examples: `continued`, `invalid_session`, `expired_session`
- **Validation rules**:
  - Continuation succeeds only if the `session_id` came from a successful initialize response and the session remains valid.
  - Continuation attempts using non-issued, expired, or unknown session identifiers must fail through the existing session-state failure contract.
- **Relationships**:
  - References one `Hosted Session` when valid.

### 6. Lifecycle Verification Record

- **Purpose**: Captures automated or manual evidence that initialize/session behavior matches the contract.
- **Fields**:
  - `check_name`
    - Type: string
    - Required: yes
  - `flow_stage`
    - Type: string
    - Required: yes
    - Examples: `initialize-failure`, `initialize-success`, `continuation`, `retry-success`
  - `result`
    - Type: success/fail outcome
    - Required: yes
  - `header_observed`
    - Type: boolean
    - Required: yes
    - Meaning: whether `MCP-Session-Id` was observed on the response being verified
  - `usable_session_state`
    - Type: boolean
    - Required: yes
    - Meaning: whether continuation state existed for the verified flow
  - `evidence`
    - Type: descriptive payload or reference
    - Required: yes
- **Validation rules**:
  - Failure-path records must prove both header absence and lack of usable session state.
  - Success-path records must prove header presence and usable continuation state.

## Relationships Summary

- One `Initialize Request` yields one `Initialize Outcome`.
- One accepted `Initialize Outcome` creates one `Hosted Session` and one `Continuation Session Identifier`.
- One rejected `Initialize Outcome` creates neither `Hosted Session` nor `Continuation Session Identifier`.
- One valid `Continuation Session Identifier` enables one or more `Continuation Attempt` records while the session remains valid.
- `Lifecycle Verification Record` proves the expected relationship between initialize outcomes and continuation behavior.

## State Transitions

### Failed Initialize Path

1. Client sends `Initialize Request`.
2. Hosted or protocol validation rejects the request.
3. `Initialize Outcome.status = rejected`.
4. No `Hosted Session` is created.
5. No `Continuation Session Identifier` is issued.

### Successful Initialize Path

1. Client sends `Initialize Request`.
2. Hosted and protocol validation accept the request.
3. `Initialize Outcome.status = accepted`.
4. One `Hosted Session` is created.
5. One `Continuation Session Identifier` is issued on the initialize response.

### Retry After Failure

1. One `Initialize Request` is rejected.
2. Client sends a later corrected `Initialize Request`.
3. Later request is accepted.
4. Session creation occurs only for the later accepted request.
5. Continuation begins only from the later issued session identifier.

### Continuation With Invalid Session

1. Client sends a continuation request with a non-issued, expired, or unknown session identifier.
2. Service rejects the continuation attempt.
3. No tool success is reported for that continuation path.
