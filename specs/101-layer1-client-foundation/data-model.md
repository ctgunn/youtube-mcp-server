# Data Model: YT-101 Layer 1 Shared Client Foundation

## Entity: Layer 1 Wrapper Definition

**Purpose**: Describes one internal wrapper around a YouTube upstream operation.

**Fields**:

- `resource_name`: The upstream resource or service area being addressed
- `operation_name`: The specific operation the wrapper performs
- `request_shape`: The expected request fields and required combinations
- `auth_mode`: One of `api_key`, `oauth_required`, or `conditional`
- `quota_cost`: The official quota-unit cost recorded for maintainer review
- `lifecycle_state`: Current lifecycle note such as active, deprecated, limited, or inconsistent-docs
- `path_shape`: The upstream path or route pattern recorded for review
- `http_method`: The upstream method recorded for review
- `notes`: Maintainer-facing notes about availability, limitations, or official-document inconsistencies

**Validation Rules**:

- `resource_name`, `operation_name`, `auth_mode`, and `quota_cost` are required
- `auth_mode` must be one of the supported contract values
- `quota_cost` must be present before a wrapper is considered complete
- `lifecycle_state` must be present whenever deprecation, availability limits, or doc inconsistencies materially affect usage

**Relationships**:

- Uses one `Shared Request Contract`
- Produces either a typed wrapper result or a `Normalized Upstream Failure`
- May be consumed by one or more `Higher-Layer Consumers`
- Implemented by the representative wrapper module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`

## Entity: Shared Request Contract

**Purpose**: Governs how all Layer 1 wrappers execute upstream requests consistently.

**Fields**:

- `request_executor`: Shared execution path for upstream requests
- `auth_policy`: Shared auth selection and credential injection rules
- `retry_policy`: Shared retry/backoff rules and retryable-failure classification
- `logging_hooks`: Shared request/response observability callbacks
- `error_normalizer`: Shared conversion from upstream failures to normalized failures

**Validation Rules**:

- Every wrapper must bind to exactly one shared request contract
- Logging and error-normalization hooks must be available for every execution path
- Retry behavior must distinguish retryable and non-retryable outcomes

**Relationships**:

- Supports many `Layer 1 Wrapper Definitions`
- Emits `Normalized Upstream Failures`
- Implemented across `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/executor.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/auth.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/retry.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/errors.py`

## Entity: Normalized Upstream Failure

**Purpose**: Represents a stable internal failure shape for higher-layer consumers.

**Fields**:

- `category`: Error category such as auth, validation, not-found, rate-limit, transient, or upstream-service
- `message`: Maintainer-usable failure explanation
- `retryable`: Whether the failure can be retried safely under policy
- `upstream_status`: Preserved upstream status or equivalent category when available
- `details`: Optional structured context safe for logs and tests

**Validation Rules**:

- `category`, `message`, and `retryable` are required
- Sensitive values must not be copied into logs or exposed details

**Relationships**:

- Produced by the `Shared Request Contract`
- Consumed by `Higher-Layer Consumers`
- Implemented by the normalized error model in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/errors.py`

## Entity: Higher-Layer Consumer

**Purpose**: Represents a later internal or public workflow that depends on typed Layer 1 methods instead of raw upstream request logic.

**Fields**:

- `consumer_name`: Maintainer-facing identifier for the dependent workflow
- `required_wrappers`: The set of Layer 1 wrappers the consumer depends on
- `composition_rules`: Ordering or combination rules when multiple wrappers are used
- `failure_handling_rules`: Expected handling of normalized upstream failures

**Validation Rules**:

- Consumers must depend on typed Layer 1 methods rather than raw request construction
- Consumers that compose multiple wrappers must use normalized failures consistently

**Relationships**:

- Depends on one or more `Layer 1 Wrapper Definitions`
- Receives failures through `Normalized Upstream Failure`
- Represented by the proof-point consumer at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

## State Transitions

### Wrapper Definition Lifecycle

1. `draft`: Wrapper shape is being defined and metadata may be incomplete
2. `reviewable`: Required metadata, auth mode, quota cost, and lifecycle notes are present
3. `executable`: Wrapper is bound to the shared request contract and passes representative tests
4. `reusable`: Wrapper is proven usable by at least one representative higher-layer consumer

### Failure Handling Lifecycle

1. Upstream issue occurs during shared execution
2. Shared request contract classifies the failure
3. Error normalizer emits a `Normalized Upstream Failure`
4. Consumer handles the normalized result according to retry and failure rules
