# Research: FND-011 Tool Metadata + Invocation Result Alignment

## Phase 0 Research Summary

### Decision: Expand `tools/list` to return full MCP-facing tool definitions, including input schema, instead of the current name-and-description-only descriptors
Rationale: The current registry implementation in `src/mcp_server/tools/dispatcher.py`
stores `inputSchema` for each tool but drops it from `list_tools()`. FND-011
exists specifically to expose complete tool metadata so MCP clients can prepare
valid calls from discovery output alone.
Alternatives considered:
- Keep discovery limited to `name` and `description`: rejected because it
  fails the feature goal and leaves clients dependent on out-of-band docs.
- Add a separate metadata endpoint: rejected because the project already
  centers discovery on `tools/list` and one MCP endpoint.

### Decision: Keep the registry contract centered on `name`, `description`, `inputSchema`, and handler, and validate those fields at registration time
Rationale: The current dispatcher already requires description, schema, and
handler, which is enough to support FND-011 without widening scope. Strengthen
that registration contract instead of inventing a second tool-definition model.
Alternatives considered:
- Introduce a new metadata wrapper object only for MCP exposure: rejected
  because it duplicates the registry source of truth and increases drift risk.
- Accept partially defined tools and patch metadata later: rejected because
  clients should never discover incomplete tools as valid.

### Decision: Return successful tool results as MCP content items that preserve structured meaning, not only one JSON string blob
Rationale: The current `_serialize_tool_result()` in
`src/mcp_server/protocol/methods.py` serializes every successful result into a
single text item. FND-011 requires aligned result content for downstream agent
consumption, so the success path should emit stable MCP content while retaining
structured information from baseline tools.
Alternatives considered:
- Keep every result as plain text JSON: rejected because it preserves the
  simplified wrapper behavior this feature is meant to replace.
- Return raw Python dictionaries directly in the `result`: rejected because
  the result must remain MCP content-oriented and client-consumable.

### Decision: Preserve `server_list_tools` parity with `tools/list` by sourcing both from the same registry metadata path
Rationale: Existing tests already compare `server_list_tools` with `tools/list`.
That parity should remain after discovery grows richer so the baseline tools
continue to function as regression evidence rather than diverging examples.
Alternatives considered:
- Let `server_list_tools` remain a legacy summary view: rejected because it
  would create two conflicting discovery contracts for the same tool catalog.
- Remove `server_list_tools`: rejected because the feature spec requires
  baseline tools to remain discoverable and invokable without regression.

### Decision: Drive the feature with failing unit, contract, and integration tests before implementation
Rationale: Current tests such as `tests/unit/test_list_tools_method.py` and
`tests/integration/test_mcp_request_flow.py` already codify the present
contract boundary. FND-011 must begin by rewriting those expectations to fail
until discovery metadata and tool result content are aligned.
Alternatives considered:
- Add new assertions after code changes: rejected by the constitution's
  mandatory Red-Green-Refactor workflow.
- Limit coverage to unit tests around the dispatcher: rejected because the
  externally visible MCP contract must also be proven at protocol and hosted
  integration boundaries.

### Decision: Keep the hosted `/mcp` transport and FND-010 request/error contract unchanged while aligning only successful tool discovery and tool result shapes
Rationale: FND-010 already established the protocol-native request and error
contract. FND-011 should build on that foundation by changing only the MCP
tool metadata and successful result content carried over the existing transport.
Alternatives considered:
- Revisit initialize or protocol error semantics in the same slice: rejected
  because that would duplicate FND-010 scope and blur acceptance criteria.
- Introduce transport-specific result variants: rejected because clients need
  the same discovery and result shapes across local and hosted flows.

## Dependencies and Integration Patterns

- Dependency: Existing tool registry in `src/mcp_server/tools/dispatcher.py`.
  - Pattern: Promote the stored registry schema into the MCP-facing discovery
    contract and keep one source of truth for tool definitions.
- Dependency: Existing protocol method routing in `src/mcp_server/protocol/methods.py`.
  - Pattern: Replace the current text-only success serializer with aligned
    MCP content shaping while leaving FND-010 request and error flow intact.
- Dependency: Baseline tools and their regression tests.
  - Pattern: Use `server_ping`, `server_info`, and `server_list_tools` as the
    minimum proof set for discovery completeness and result stability.
- Integration target: Hosted and local MCP flows.
  - Pattern: Verify `tools/list` and `tools/call` return the same logical
    contract in direct app handling and hosted request execution paths.

## Red-Green-Refactor Plan

### Red
- Replace existing discovery assertions with failing checks that each listed
  tool includes `name`, `description`, and `inputSchema`.
- Add failing tests that verify `server_list_tools` returns the same richer
  descriptors as `tools/list`.
- Add failing tests that verify successful baseline tool invocations return
  aligned MCP content structures that preserve structured meaning instead of
  only a single JSON string.
- Add failing integration and contract checks for local and hosted `tools/list`
  and `tools/call` flows carrying the aligned metadata/result shapes.

### Green
- Update the registry to expose complete tool definitions through one metadata
  path.
- Update successful tool-call result shaping to emit the minimum aligned MCP
  content structure needed for baseline tools and future tool extension.
- Keep initialize, protocol error behavior, readiness, and hosted transport
  semantics unchanged while making the new discovery and success-result tests
  pass.

### Refactor
- Consolidate duplicated descriptor-building and result-shaping logic across
  registry, baseline tool handlers, and protocol methods.
- Remove transitional assumptions that discovery only needs summary fields or
  that successful tool results should always be text-only JSON.
- Re-run the full regression suite to confirm no regressions in earlier
  foundation slices.

## Resolved Clarifications

No `NEEDS CLARIFICATION` markers remain. The current FND-010 contract, the
existing dispatcher and protocol code, and the feature spec provide enough
context to resolve the design decisions for this slice.
