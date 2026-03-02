# Data Model: Tool Registry + Dispatcher (FND-002)

## Entity: ToolDefinition
Description: Canonical definition for a tool that can be registered and invoked.

Fields:
- `name` (string, required): Client-visible tool identifier.
- `normalizedName` (string, required): Normalized identifier used for uniqueness and lookup.
- `description` (string, required): Human-readable capability summary.
- `inputContract` (object, required): Contract used to validate invocation arguments.
- `handlerBinding` (callable, required): Executable behavior for valid invocations.

Validation rules:
- `name`, `description`, `inputContract`, and `handlerBinding` are all required.
- `normalizedName` MUST be unique across active registry entries.
- Missing or invalid fields MUST produce structured validation errors.

## Entity: ToolRegistry
Description: In-memory collection managing active `ToolDefinition` entries.

Fields:
- `entries` (map, required): Keyed by `normalizedName`.
- `orderedDescriptors` (array, derived): Deterministic list view for tool discovery.

Validation rules:
- Registering a duplicate `normalizedName` MUST be rejected.
- List responses SHOULD be deterministic for stable client behavior.

## Entity: DispatchRequest
Description: Invocation input that identifies the target tool and arguments.

Fields:
- `toolName` (string, required): Requested tool identifier from client request.
- `arguments` (object, optional): Arguments validated against `inputContract`.
- `requestId` (string | number | null, optional): Correlation identifier propagated in response metadata.

Validation rules:
- `toolName` MUST be non-empty.
- `arguments` MUST be an object when provided.
- Unknown `toolName` MUST map to `RESOURCE_NOT_FOUND`.

## Entity: DispatchResult
Description: Output envelope payload produced after dispatch evaluation.

Fields:
- `success` (boolean, required)
- `toolName` (string, required on success)
- `result` (object | array | primitive | null, required on success)
- `error` (object, required on failure)
  - `code` (string)
  - `message` (string)
  - `details` (object | null)

Validation rules:
- Successful dispatch MUST include executed tool result.
- Failed dispatch MUST include structured error and no stack trace details.

## Relationships

- `ToolRegistry` contains multiple `ToolDefinition` entries.
- `DispatchRequest.toolName` resolves to one `ToolDefinition` via normalized lookup.
- `DispatchResult` is derived from either:
  - successful `handlerBinding` execution, or
  - structured error mapping for validation/lookup/execution failures.

## State Transitions

- Registration attempt -> validate fields -> normalize name ->
  add to registry OR reject with structured error.
- Dispatch attempt -> validate request shape -> normalize lookup key ->
  locate entry -> validate arguments -> execute handler -> emit success envelope.
- Dispatch failure path -> unknown tool / invalid arguments / runtime failure ->
  map to structured failure envelope.
