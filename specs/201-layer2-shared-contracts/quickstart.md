# Quickstart: YT-201 Shared YouTube Scaffolding and Contracts

## Purpose

Use this feature to establish the shared YouTube contracts and scaffolding required before individual YouTube Data API endpoint MCP tools are exposed publicly.

YT-201 defines shared rules for naming, upstream identity, auth and quota visibility, input mapping, near-raw result conventions, safe errors, resource-family placement, representative examples, tests, and docstrings. It does not implement concrete endpoint-backed tools.

## Prerequisites

- Work from `/Users/ctgunn/Projects/youtube-mcp-server` on branch `201-layer2-shared-contracts`
- Keep the slice limited to shared YouTube scaffolding and representative examples
- Do not add concrete endpoint-backed YouTube tools in this slice
- Preserve existing MCP registry, dispatcher, hosted transport, retrieval tools, and Layer 1 endpoint behavior
- Depend on Layer 1 resource-family capabilities for upstream request execution and normalization
- Add or preserve reStructuredText docstrings for every new or changed Python function

## Red Phase

1. Add failing contract tests proving a representative YouTube tool contract is incomplete without public name, upstream identity, auth mode, quota cost, input mapping, response convention, caveat handling, and safe error categories.
2. Add failing unit tests for deterministic `resource_method` naming, including camelCase method suffixes and rejection of redundant `youtube_` naming.
3. Add failing or characterization tests for representative endpoint shapes:
   - simple read
   - paginated list
   - camelCase method
   - OAuth-only
   - mutation
   - upload or media-related
   - high quota
   - deprecated or availability-constrained
4. Add failing documentation or placement checks showing that future endpoint authors need clear resource-family locations for definitions, handlers, schemas, tests, examples, and caveats.

## Green Phase

1. Add the minimum shared YouTube contract records or helpers needed to satisfy the failing metadata and naming tests.
2. Add representative example records or fixtures for the required endpoint shapes without implementing actual endpoint tool behavior.
3. Add shared validation expectations for auth mode, quota visibility, caveats, input mapping, near-raw response conventions, and safe errors.
4. Add the minimum registration or discovery scaffolding needed to prove future YouTube tools can fit the existing MCP tool registry.
5. Keep shared YouTube code centralized and endpoint-specific behavior out of this slice.

## Refactor Phase

1. Remove duplicate example metadata or repeated contract wording from shared helpers.
2. Keep endpoint-specific facts in representative examples and shared rules in shared scaffolding.
3. Verify every new or changed Python function has a reStructuredText docstring.
4. Confirm no secrets, tokens, stack traces, or raw media payloads appear in examples, logs, errors, or tests.
5. Run focused checks, then full repository verification.

## Suggested Verification Commands

From `/Users/ctgunn/Projects/youtube-mcp-server`:

```bash
python3 -m pytest tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/integration/test_youtube_tool_registration.py
python3 -m pytest
python3 -m ruff check .
```

Implemented shared scaffolding files:

- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py`

Focused validation now covers shared contract metadata, naming, representative
catalog examples, input/response/error conventions, resource-family placement,
and dispatcher registration without endpoint execution.

When contract catalog coverage is added, include:

```bash
python3 -m pytest tests/contract/test_youtube_tool_catalog_contract.py
```

## Review Checklist

- Shared public YouTube tool naming rules are defined and tested
- Representative examples cover the required endpoint shapes
- Auth modes, quota costs, and caveats are visible before invocation
- Input contracts stay close to upstream request concepts
- Response conventions preserve near-raw upstream semantics
- Error categories are stable and MCP-safe
- Resource-family placement rules are clear for later endpoint slices
- No concrete endpoint tool behavior is added in this slice
- New or changed Python functions have reStructuredText docstrings
- Final evidence includes `python3 -m pytest` and `python3 -m ruff check .`
