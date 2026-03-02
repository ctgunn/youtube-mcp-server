# Quickstart: FND-001 MCP Transport + Handshake

## Objective
Validate foundation MCP flow for initialize, list tools, and invoke tool using
Red-Green-Refactor TDD execution.

## Prerequisites
- Python 3.11+
- Feature branch: `001-mcp-transport-handshake`
- Source tree present at `src/mcp_server`

## Red Phase (write failing tests first)

1. Add/adjust contract tests for:
   - initialize success and malformed initialize request
   - tools/list success response envelope
   - tools/call success and unknown tool error envelope
2. Add/adjust unit tests for:
   - method routing and unsupported method handling
   - error mapping shape (`code`, `message`, optional `details`)
3. Run red tests and verify failure state before implementation changes:

```bash
python3 -m unittest discover -s tests/unit -p 'test_*.py'
```

## Green Phase (minimal implementation)

1. Implement `/mcp` transport handler.
2. Implement method router for `initialize`, `tools/list`, and `tools/call`.
3. Implement response envelope and error mapper.
4. Re-run targeted suites:

```bash
python3 -m unittest discover -s tests/unit -p 'test_*.py'
python3 -m unittest discover -s tests/contract -p 'test_*.py'
```

## Refactor Phase (behavior-preserving cleanup)

1. Extract reusable envelope and dispatch helpers.
2. Keep validation/error handling centralized.
3. Re-run complete FND-001 suite:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

Latest local run result:
- 15 tests run, 15 passed.

## Manual Flow Validation

1. Create app object (`create_app`) and call `handle("/mcp", payload)`.
2. Submit initialize payload.
3. Submit tools/list payload.
4. Submit tools/call payload for `server_ping`.

Success criteria:
- Each response follows standard envelope shape.
- Unknown tool invocation returns `RESOURCE_NOT_FOUND`.
- No client-visible stack traces.
