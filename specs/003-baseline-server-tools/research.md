# Research: Baseline Server Tools (FND-003)

## Phase 0 Research Summary

### Decision: Register all baseline tools through the existing dispatcher registry lifecycle
Rationale: FND-003 depends on FND-002 and must preserve transport-independence; using registry registration keeps new tools discoverable/invokable without protocol router branching.
Alternatives considered:
- Hard-code baseline tool responses in method routing: rejected because it bypasses the dispatcher contract.
- Keep only `server_ping` as a special default tool: rejected because FND-003 requires all three baseline tools listed and invokable.

### Decision: Keep baseline tool inputs minimal and deterministic
Rationale: Baseline tools are smoke-test utilities and should remain reliable under empty argument payloads.
Alternatives considered:
- Add optional filtering or debug flags to baseline tools: rejected because it expands scope and test surface without user value for this slice.
- Require non-empty arguments for all baseline tools: rejected because it complicates operator verification flows.

### Decision: Source `server_info` output from startup/runtime metadata with safe defaults
Rationale: Operators need version/environment/build visibility even when optional metadata is partially unavailable.
Alternatives considered:
- Fail `server_info` if any optional field is missing: rejected because this hurts diagnostics during incomplete deployments.
- Return only static constants: rejected because it reduces release verification value.

### Decision: Implement `server_list_tools` as a tool-level reflection of active registry entries
Rationale: The tool should reflect actual runtime registration to validate extensibility and detect missing registrations during smoke tests.
Alternatives considered:
- Return a static list of baseline tool names: rejected because it can diverge from runtime truth.
- Exclude the baseline tools from their own listing: rejected because it reduces operator confidence in registration lifecycle.

### Decision: Cover baseline tools with explicit Red-Green-Refactor test sequencing
Rationale: Constitution requires TDD and integration/regression evidence for MCP-facing behavior.
Alternatives considered:
- Add handlers first and test after: rejected because this violates mandatory TDD.
- Rely only on integration tests: rejected because unit and contract coverage is needed for envelope and error guarantees.

## Dependencies and Integration Patterns

- Dependency: FND-001 MCP routing and response envelope.
  - Pattern: keep method surface unchanged and route calls through existing `tools/list` and `tools/call` paths.
- Dependency: FND-002 registry and dispatcher behavior.
  - Pattern: register baseline tools using `register_tool`; invoke through `call_tool`.
- Dependency: existing error model (`code`, `message`, optional `details`).
  - Pattern: map validation/runtime failures to standardized MCP-safe errors.

## Red-Green-Refactor Plan

### Red
- Add failing unit tests for new baseline tool handler outputs and metadata fallbacks.
- Add failing integration tests for list/invoke flows across all three baseline tools.
- Add failing contract assertions that responses for baseline tools preserve envelope shape and expected payload fields.

### Green
- Implement minimal handler logic for `server_info` and `server_list_tools` and confirm `server_ping` contract alignment.
- Register all baseline tools during dispatcher initialization/bootstrapping.
- Make only the required changes to satisfy failing tests.

### Refactor
- Consolidate shared helper logic for metadata construction and tool descriptor formatting.
- Remove duplicate test setup for baseline tool invocation flows.
- Re-run full unit, integration, and contract suites to ensure no regression.

## Resolved Clarifications

No `NEEDS CLARIFICATION` items remain. All technical context decisions are resolved for planning.
