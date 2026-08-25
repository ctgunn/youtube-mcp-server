# MCP Tool-Catalog Verification Contract

## Purpose and scope

This contract defines the internal Layer 4 verification boundary for the default MCP tool catalog. It validates existing public MCP behavior; it does not add public tools, alter client input schemas, or replace credential-gated live verification.

## Discovery contract

The suite obtains catalog membership only by submitting a JSON-RPC request with method `tools/list` to the public MCP route.

| Requirement | Contract |
| --- | --- |
| Request | JSON-RPC object with method `tools/list` and object `params`. |
| Success envelope | `result.tools` is a non-empty list of public descriptors. |
| Tool identity | Every descriptor has a non-empty, unique `name`. |
| Inventory authority | The resulting names are the sole input to catalog coverage; no duplicated hard-coded default inventory is permitted. |

## Invocation contract

For every descriptor returned by discovery, the suite submits one JSON-RPC request with method `tools/call`.

| Requirement | Contract |
| --- | --- |
| Request parameters | `params.name` equals the discovered public name; `params.arguments` is the fixture's JSON object. |
| Successful outcome | The response has no top-level JSON-RPC error, has `result.isError` set to false, and has nonempty `result.content` containing structured content. |
| Expected-error outcome | The response has a top-level JSON-RPC error whose `error.data.category` equals the fixture's documented category. The route returns an envelope rather than allowing an exception to escape. |
| Endpoint identity | If successful structured content exposes `endpoint` and the discovered descriptor exposes `metadata.upstream.operationKey`, the values are identical. |
| Reporting | Each discovered public name is an individually reported test case. |

## Fixture completeness contract

The fixture registry contains exactly one active fixture for each discovered public name.

| Condition | Required result |
| --- | --- |
| Discovered name has no fixture | Fail and list the missing name. |
| Fixture name is not discovered | Fail and list the stale name. |
| Fixture has duplicate name, non-object arguments, missing purpose, or invalid outcome declaration | Fail before route invocation and identify the fixture. |
| Fixture expects an error | It declares one safe MCP error category. |

Fixtures are test-owned review artifacts. Discovery metadata examples may inform a fixture but are not themselves the fixture registry.

## Safety and compatibility contract

- The suite runs with no real credentials, outbound YouTube request, or destructive external mutation.
- An outbound-request guard makes unintended network activity fail the test.
- The feature makes no breaking change: client-facing `tools/list`/`tools/call` schemas, tool names, and successful result shapes remain unchanged.
- Credential-gated, read-only live smoke verification remains separate and opt-in.

## Contract validation

The focused integration suite proves discovery authority, exact fixture coverage, one public-route call per discovered tool, successful and expected-error response rules, conditional endpoint identity, no escaped process exception, and no outbound activity. `make test-tools` runs this suite; `make quality` remains the complete release evidence command.
