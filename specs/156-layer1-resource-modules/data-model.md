# Data Model: YT-156 Layer 1 Resource-Family Module Reorganization

## Resource Family Module

**Purpose**: Groups Layer 1 responsibilities for one YouTube resource family so maintainers and future tool authors can find related wrappers, metadata, validators, and normalizers without broad-file traversal.

**Fields**:

- `family_name`: Stable resource-family label, such as `captions`, `channels`, `comments`, `playlist_items`, `videos`, or `watermarks`
- `resource_names`: Upstream resource names represented by the family
- `wrapper_classes`: Typed Layer 1 wrapper classes owned by the family
- `builder_functions`: Stable functions that create wrappers for the family's operations
- `metadata_declarations`: Endpoint identity, quota cost, auth mode, path shape, and caveat notes for each operation
- `validators`: Endpoint-specific request-shape or selector validation owned by the family
- `response_normalizers`: Endpoint-specific response shaping responsibilities owned by the family when specialized handling is required

**Validation Rules**:

- Must keep all behavior equivalent to the pre-refactor endpoint contract
- Must depend on shared Layer 1 foundations rather than duplicating auth, executor, retry, observability, contract, request-construction, or error-normalization logic
- Must expose enough symbols for compatibility facades to preserve existing import paths
- Must include reStructuredText docstrings for every new or changed Python function

**Relationships**:

- Owns one or more `Layer 1 Endpoint Capability` records
- Registers zero or more `Response Normalizer Mapping` entries
- Is re-exported by one or more `Compatibility Import Surface` entries

## Layer 1 Endpoint Capability

**Purpose**: Represents one completed Layer 1 endpoint capability from YT-103 through YT-155 whose observable contract must remain unchanged.

**Fields**:

- `resource_name`: Upstream resource name
- `operation_name`: Upstream operation name
- `operation_key`: Stable internal operation key
- `http_method`: Upstream request method
- `path_shape`: Upstream endpoint path shape
- `quota_cost`: Official quota-unit cost
- `auth_mode`: Required or conditional access mode
- `request_shape`: Required, optional, and exclusive request fields
- `notes`: Maintainer-facing caveats or availability guidance
- `wrapper_builder`: Function that constructs the endpoint wrapper
- `normalizer_key`: Operation key used for specialized response handling when applicable

**Validation Rules**:

- Must preserve request validation rules, selector and filter modes, credential attachment behavior, quota-cost metadata, auth-mode metadata, response payload shape, and normalized upstream error behavior
- Must remain reachable through existing compatibility imports and resource-family access
- Must not introduce new endpoint semantics or second implementations of completed endpoint behavior

**Relationships**:

- Belongs to one `Resource Family Module`
- May use one `Response Normalizer Mapping`
- Exposes behavior through `Compatibility Import Surface`

## Response Normalizer Mapping

**Purpose**: Defines how operation-specific upstream payload handling is selected without relying on one long central conditional flow.

**Fields**:

- `operation_key`: Stable operation identifier
- `family_name`: Resource family that owns the normalizer
- `normalizer`: Callable response-shaping responsibility
- `input_requirements`: Whether the normalizer requires execution context, payload content, or both
- `fallback_behavior`: Generic object parsing behavior when no specialized normalizer is registered
- `failure_boundaries`: Normalized failure categories preserved by shared error handling

**Validation Rules**:

- Must preserve the exact successful response shape for every operation with specialized handling
- Must preserve each normalizer's existing input needs, including no-content acknowledgement handlers that use execution context without parsing payload
- Must preserve fallback behavior for operations without specialized handling
- Must make operation-to-normalizer ownership explicit enough for review
- Must not change upstream error normalization or credential behavior

**Relationships**:

- Is owned by a `Resource Family Module`
- Is selected by a dispatch mechanism during shared YouTube execution
- Produces the same result shape expected by `Layer 1 Endpoint Capability`

## Compatibility Import Surface

**Purpose**: Represents an existing import path used by downstream code and tests that must continue to expose the same Layer 1 capabilities after the refactor.

**Fields**:

- `import_path`: Existing import path, such as `mcp_server.integrations`, `mcp_server.integrations.wrappers`, or `mcp_server.integrations.youtube`
- `exported_symbols`: Wrapper classes, builder functions, transport helpers, or executor helpers exposed by that path
- `backing_family_module`: Resource-family module that now owns the implementation when applicable
- `compatibility_status`: Expected to remain compatible for this feature

**Validation Rules**:

- Existing imports must continue to resolve
- Existing exported symbol names must continue to return equivalent capabilities
- Compatibility facades must avoid circular imports
- Compatibility paths must not mask behavior changes

**Relationships**:

- Re-exports one or more `Layer 1 Endpoint Capability` records
- May delegate implementation to one or more `Resource Family Module` records

## Verification Evidence

**Purpose**: Captures the tests and review evidence required to prove the reorganization preserved behavior.

**Fields**:

- `targeted_resource_family_checks`: Focused tests for moved families
- `compatibility_import_checks`: Tests proving existing imports still work
- `normalizer_dispatch_checks`: Tests proving response mapping remains explicit and equivalent
- `full_suite_command`: Expected to be `python3 -m pytest`
- `lint_command`: Expected to be `python3 -m ruff check .`
- `docstring_review`: Confirmation that new or changed Python functions have reStructuredText docstrings

**Validation Rules**:

- Must include targeted checks before final full-suite validation
- Must include a full repository test-suite run after final code changes
- Must include lint validation after final code changes
- Must document any compatibility shims intentionally kept for downstream stability
