# Data Model: Baseline Server Tools (FND-003)

## Entity: BaselineToolDefinition
Description: Runtime registration entry for each baseline smoke-test tool.

Fields:
- `name` (string, required): Tool identifier (`server_ping`, `server_info`, `server_list_tools`).
- `normalizedName` (string, required): Normalized lookup key used by registry uniqueness checks.
- `description` (string, required): Operator-facing summary of tool purpose.
- `inputSchema` (object, required): Invocation argument contract.
- `handler` (callable, required): Tool execution function.

Validation rules:
- `name`, `description`, `inputSchema`, and `handler` are required.
- `normalizedName` MUST be unique in the active registry.
- Baseline tool input schemas MUST accept only documented fields for each tool.

## Entity: ServerPingPayload
Description: Output payload for service reachability checks.

Fields:
- `status` (string, required): Service availability indicator.
- `timestamp` (string, required): Current invocation timestamp.

Validation rules:
- `status` MUST be non-empty.
- `timestamp` MUST be present on every successful invocation.

## Entity: ServerInfoPayload
Description: Output payload for runtime metadata verification.

Fields:
- `version` (string, required): Server version identifier.
- `environment` (string, required): Active deployment/runtime profile.
- `build` (object, required): Build metadata container.
  - `commit` (string, optional)
  - `buildTime` (string, optional)
  - `buildId` (string, optional)

Validation rules:
- `version` and `environment` MUST be present, with fallback-safe values if unset.
- `build` object MUST be present even if optional nested fields are missing.

## Entity: ToolSummaryEntry
Description: Tool listing entry returned by `server_list_tools`.

Fields:
- `name` (string, required)
- `description` (string, required)

Validation rules:
- Returned list MUST include all currently registered tools.
- Ordering SHOULD remain deterministic for stable smoke-test assertions.

## Entity: ToolInvocationEnvelope
Description: Standardized response envelope for baseline tool invocation outcomes.

Fields:
- `success` (boolean, required)
- `data` (object | array | primitive | null, required)
- `meta` (object, required)
  - `requestId` (string | number | null, optional)
- `error` (object | null, required)
  - `code` (string, required on failure)
  - `message` (string, required on failure)
  - `details` (object | null, optional)

Validation rules:
- Success responses MUST set `success=true` and `error=null`.
- Failure responses MUST set `success=false` and provide structured `error` fields.
- No failure response may include stack traces.

## Relationships

- `BaselineToolDefinition` entries are held by the existing registry and exposed via tool list flows.
- `server_ping` resolves to `ServerPingPayload` within `ToolInvocationEnvelope`.
- `server_info` resolves to `ServerInfoPayload` within `ToolInvocationEnvelope`.
- `server_list_tools` resolves to an array of `ToolSummaryEntry` within `ToolInvocationEnvelope`.

## State Transitions

- Service boot/startup -> baseline tool registration -> tools discoverable via list paths.
- Invocation request -> dispatcher validation -> handler execution -> success envelope.
- Invocation request with invalid target/args/runtime issue -> standardized error envelope.
