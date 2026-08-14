# Quickstart: YT-317 Channel Statistics

## Goal

Use this guide to verify that planning is complete before generating implementation tasks for `channels_getStatistics`.

## Review the Plan Artifacts

```bash
sed -n '1,280p' /Users/ctgunn/Projects/youtube-mcp-server/specs/317-channels-get-statistics/spec.md
sed -n '1,420p' /Users/ctgunn/Projects/youtube-mcp-server/specs/317-channels-get-statistics/plan.md
sed -n '1,360p' /Users/ctgunn/Projects/youtube-mcp-server/specs/317-channels-get-statistics/research.md
sed -n '1,320p' /Users/ctgunn/Projects/youtube-mcp-server/specs/317-channels-get-statistics/data-model.md
sed -n '1,360p' /Users/ctgunn/Projects/youtube-mcp-server/specs/317-channels-get-statistics/contracts/channels-get-statistics-contract.md
```

## Confirm the Contract Before Tasking

- `channels_getStatistics` requires exactly one nonblank `channelId` and accepts no optional fields.
- The tool performs one direct lower-level lookup using only the source `statistics` group.
- The result always gives callers an entry for `subscriberCount`, `videoCount`, and `viewCount`.
- A source-reported `"0"` is an available value; a source-flagged hidden subscriber count is `hidden` with no numeric value; a missing or malformed metric is `unavailable` with no numeric value.
- Values retain their source decimal representation; the tool does not calculate rates, trends, estimates, comparisons, or other derived analytics.
- The result documents source rounding for subscriber counts, the public-only scope of video counts, and the source's current channel-view definition.
- An unavailable channel produces `unavailable_resource`, distinct from a retrievable channel with hidden or unavailable metrics.
- The feature introduces no persistence, new source integration, fan-out, pagination, enrichment, ranking, or transport change.

## Expected Red-Green-Refactor Flow

1. **Red**: Add failing unit, contract, integration, and routing tests for validation, exact source request, available and zero counts, hidden subscriber counts, unavailable metrics, safe errors, discovery, and default registration.
2. **Green**: Add only the descriptor, validation, one-lookup adapter, metric normalization, safe error mapping, exports, registration, and any necessary default fixture support needed to pass those tests.
3. **Refactor**: Consolidate repeated metric and sanitization behavior, retain reStructuredText docstrings on every changed Python function, then rerun focused and full checks.

## Planned Verification Commands

Run focused checks during implementation:

```bash
PYTHONPATH=src python3 -m pytest \
  tests/unit/test_youtube_composed_channels.py \
  tests/contract/test_youtube_composed_channels_contract.py \
  tests/integration/test_youtube_composed_tool_registration.py \
  tests/integration/test_youtube_tool_registration.py \
  tests/unit/test_method_routing.py
```

Run these after the final code change:

```bash
PYTHONPATH=src python3 -m pytest
PYTHONPATH=src python3 -m ruff check .
```

## Review Evidence

Pull-request review should include:

- The matched seed slice, `YT-317`.
- Failing-test evidence before implementation and passing focused-test evidence after it.
- Discovery output proving the concrete `channels_getStatistics` descriptor is registered without a representative-only marker.
- Result evidence for all expected available metrics, a reported zero, a hidden subscriber count, missing metrics with no numeric value, and source-interpretation caveats.
- Confirmation that each invocation makes exactly one lower-level channel statistics lookup.
- Safe unavailable, authorization, quota, and upstream error evidence without sensitive diagnostics.
- Passing full-suite and lint output.
- Confirmation that all new or changed Python functions have reStructuredText docstrings.
