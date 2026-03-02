# Quickstart: FND-002 Tool Registry + Dispatcher

## Objective
Implement and validate registry/dispatcher lifecycle behavior while preserving
MCP envelope compatibility and strict Red-Green-Refactor workflow.

## Prerequisites
- Python 3.11+
- Feature branch: `002-tool-registry-dispatcher`
- Existing FND-001 transport and method routing baseline

## Red Phase (write failing tests first)

1. Add failing unit tests for:
   - required registration fields,
   - duplicate registration rejection,
   - successful dispatch routing,
   - invalid argument handling,
   - unknown tool mapping to `RESOURCE_NOT_FOUND`.
2. Add/adjust contract tests for list/call envelope behavior and unknown-tool errors.
3. Run targeted tests and confirm failures before implementation:

```bash
python3 -m unittest discover -s tests/unit -p 'test_*.py'
python3 -m unittest discover -s tests/contract -p 'test_*.py'
```

## Green Phase (minimal implementation)

1. Implement registry registration and lookup lifecycle.
2. Implement dispatcher input validation and handler routing.
3. Map unknown tools and invalid input to structured MCP-safe errors.
4. Re-run targeted suites until green:

```bash
python3 -m unittest discover -s tests/unit -p 'test_*.py'
python3 -m unittest discover -s tests/integration -p 'test_*.py'
python3 -m unittest discover -s tests/contract -p 'test_*.py'
```

## Refactor Phase (behavior-preserving cleanup)

1. Extract shared normalization and validation helpers.
2. Keep transport layer free from tool-specific registration logic.
3. Re-run full regression suite:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

Latest local run result:
- 26 tests run, 26 passed.

## Manual Flow Validation

1. Register at least one baseline tool with required attributes.
2. Invoke `tools/list` and verify the tool appears in the response.
3. Invoke `tools/call` for the registered tool with valid arguments.
4. Invoke `tools/call` for an unknown tool name.

Success criteria:
- Registered tools are discoverable and invokable.
- Unknown tool calls return `RESOURCE_NOT_FOUND` with `details.toolName`.
- Invalid arguments return structured validation errors (`INVALID_ARGUMENT`).
- No response exposes stack traces.
