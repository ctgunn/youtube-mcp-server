# Quickstart: YT-202 Layer 2 Tool Metadata, Naming, and Quota Standards

## Purpose

Use this feature to tighten the shared Layer 2 metadata standard before individual endpoint-backed YouTube Data API MCP tools are implemented.

YT-202 defines required metadata fields, deterministic public naming, quota disclosure, auth and availability visibility, usage-note expectations, response-boundary classification, representative examples, tests, and docstring obligations. It does not implement concrete endpoint-backed tools.

## Prerequisites

- Work from `/Users/ctgunn/Projects/youtube-mcp-server` on branch `202-layer2-metadata-standards`
- Keep the slice limited to shared metadata standards, representative examples, and validation expectations
- Do not add concrete endpoint-backed YouTube tools in this slice
- Reuse YT-201 shared Layer 2 scaffolding under `src/mcp_server/tools/youtube_common/`
- Preserve existing MCP registry, dispatcher, hosted transport, retrieval tools, and Layer 1 endpoint behavior
- Add or preserve reStructuredText docstrings for every new or changed Python function

## Red Phase

1. Add failing contract tests proving representative Layer 2 tool metadata is incomplete without:
   - public MCP tool name
   - upstream resource and method
   - stable operation key
   - official quota-unit cost
   - auth mode
   - availability state
   - description quota visibility
   - usage-note quota visibility
   - response-boundary classification
2. Add failing naming tests for at least 10 representative resource-method pairs, including camelCase methods such as `comments.setModerationStatus`, `videos.getRating`, and `videos.reportAbuse`.
3. Add failing quota visibility checks proving cost appears in metadata, descriptions, and usage notes, with explicit high-cost warnings for expensive endpoints.
4. Add failing response-boundary checks for near-raw, lightly reshaped, and out-of-scope Layer 3-style examples.
5. Add failing or characterization checks that confirm examples remain non-executing standards artifacts unless a later endpoint slice implements behavior.

## Green Phase

1. Extend the minimum shared metadata record and validation helpers needed to satisfy required field checks.
2. Add or tighten naming derivation so public names follow `resource_method`, omit `youtube_`, preserve meaningful camelCase suffixes, and remain deterministic.
3. Add quota disclosure fields or validation so official cost is visible in metadata, description text, and usage notes.
4. Add auth-mode and availability-state declarations with safe caller-facing caveat notes.
5. Add response-boundary classification metadata for near-raw, lightly reshaped, and out-of-scope examples.
6. Add at least 10 representative non-executing metadata examples covering the required endpoint shapes.

## Refactor Phase

1. Remove duplicated quota, auth, caveat, and response-boundary wording from examples and helpers.
2. Keep YT-202 focused on metadata standards; leave broad input, layout, and error scaffolding with YT-201.
3. Confirm every new or changed Python function has a reStructuredText docstring.
4. Confirm public metadata, examples, docs, tests, logs, and errors do not expose secrets, tokens, stack traces, signed URLs, or unsafe raw media payloads.
5. Run focused checks, then full repository verification.

## Suggested Verification Commands

From `/Users/ctgunn/Projects/youtube-mcp-server`:

```bash
python3 -m pytest tests/unit/test_layer2_shared_scaffolding.py tests/contract/test_layer2_shared_contract.py tests/contract/test_layer2_tool_catalog_contract.py tests/integration/test_layer2_tool_registration.py
python3 -m pytest
python3 -m ruff check .
```

## Planned Shared Standards Files

- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py`

## Implemented Standards Summary

- `Layer2ToolContract` exposes availability state, usage notes, safe public metadata validation, and response-boundary metadata.
- `AvailabilityState` records active, deprecated, unavailable, region-constrained, owner-only, media-constrained, and documentation-caveat endpoint states.
- `ResponseBoundary` and `ResponseBoundaryKind` classify representative outputs as near-raw, lightly reshaped, or out of Layer 2 scope.
- `REPRESENTATIVE_LAYER2_CONTRACTS` includes non-executing examples covering read, paginated, camelCase, OAuth-only, mixed-auth, mutation, media, high-quota, constrained, lookup, download, upload, and acknowledgment shapes.
- `build_representative_tool_descriptor()` exposes standards metadata for discovery-style validation while keeping the handler representative-only.

## Review Checklist

- Required metadata fields are present for each representative example
- Public names derive from resource-method pairs without `youtube_`
- CamelCase upstream method suffixes remain recognizable
- Quota cost is visible in metadata, descriptions, and usage notes
- High-cost endpoints include explicit warnings
- Auth mode and availability state are visible before invocation
- Caveats are safe and caller-facing
- Response-boundary classification distinguishes near-raw, lightly reshaped, and out-of-scope behavior
- Representative examples remain non-executing standards examples
- New or changed Python functions have reStructuredText docstrings
- Final evidence includes `python3 -m pytest` and `python3 -m ruff check .`
