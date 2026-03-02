# Quickstart: FND-003 Baseline Server Tools

## Objective
Implement baseline non-YouTube smoke tools and verify they are discoverable and
invokable via existing MCP list/call flows while preserving standard response
and error contracts.

## Prerequisites
- Python 3.11+
- Feature branch: `003-baseline-server-tools`
- Existing FND-001 and FND-002 foundations available

## Red Phase (write failing tests first)

1. Add failing unit tests for:
   - `server_info` metadata payload shape and fallback handling.
   - `server_list_tools` output shape and required baseline entries.
   - `server_ping` contract alignment (`status`, `timestamp`).
2. Add failing integration/contract assertions that:
   - all baseline tools are returned by discovery,
   - each baseline tool is invokable through `tools/call`,
   - envelope shape is preserved for both success and failure paths.
3. Run targeted suites and confirm failures:

```bash
python3 -m unittest discover -s tests/unit -p 'test_*.py'
python3 -m unittest discover -s tests/integration -p 'test_*.py'
python3 -m unittest discover -s tests/contract -p 'test_*.py'
```

## Green Phase (minimal implementation)

1. Register `server_info` and `server_list_tools` alongside `server_ping`.
2. Implement minimal handler behavior to satisfy test-defined contracts.
3. Keep method routing and transport interfaces unchanged.
4. Re-run targeted suites until all pass:

```bash
python3 -m unittest discover -s tests/unit -p 'test_*.py'
python3 -m unittest discover -s tests/integration -p 'test_*.py'
python3 -m unittest discover -s tests/contract -p 'test_*.py'
```

## Refactor Phase (behavior-preserving cleanup)

1. Consolidate shared helper code for baseline payload construction.
2. Remove duplicate test setup and improve baseline-tool test readability.
3. Run full regression suite:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Manual Validation Flow

1. Start the local service.
2. Send `tools/list` and confirm baseline tools appear.
3. Invoke `server_ping`, `server_info`, and `server_list_tools` via `tools/call`.
4. Invoke an unknown tool and confirm standardized error response.

Success criteria:
- All three baseline tools are discoverable and invokable.
- Baseline outputs match documented contracts.
- Unknown tool calls still return `RESOURCE_NOT_FOUND`.
- Response envelope remains consistent across all calls.

## Latest Validation Evidence

- Unit suite: `python3 -m unittest discover -s tests/unit -p 'test_*.py'` -> 24 passed
- Integration suite: `python3 -m unittest discover -s tests/integration -p 'test_*.py'` -> 6 passed
- Contract suite: `python3 -m unittest discover -s tests/contract -p 'test_*.py'` -> 7 passed
- Full regression: `python3 -m unittest discover -s tests -p 'test_*.py'` -> 37 passed
