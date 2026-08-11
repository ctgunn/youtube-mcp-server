# Quickstart: YT-305 Channel Details

## Goal

Use this guide to verify that planning is complete before generating implementation tasks for `channels_getChannel`.

## Review the Plan Artifacts

```bash
sed -n '1,320p' /Users/ctgunn/Projects/youtube-mcp-server/specs/305-channels-get-channel/spec.md
sed -n '1,420p' /Users/ctgunn/Projects/youtube-mcp-server/specs/305-channels-get-channel/plan.md
sed -n '1,320p' /Users/ctgunn/Projects/youtube-mcp-server/specs/305-channels-get-channel/research.md
sed -n '1,320p' /Users/ctgunn/Projects/youtube-mcp-server/specs/305-channels-get-channel/data-model.md
sed -n '1,420p' /Users/ctgunn/Projects/youtube-mcp-server/specs/305-channels-get-channel/contracts/channels-get-channel-contract.md
```

## Confirm the Contract Before Tasking

- `channels_getChannel` accepts exactly one nonblank `channelId` and rejects all unknown fields.
- The result is one normalized channel profile with public metadata and per-field provenance.
- The core lookup is one channel read; latest-video enrichment makes at most one one-item uploads-playlist read.
- Public email addresses and links are cautious derived values from returned public channel material only; they are not verified contact or ownership data.
- Creator-versus-brand classification is `creator`, `brand`, or `unknown`, has safe signal identifiers, and is explicitly non-canonical.
- No latest public video is a successful `unavailable` enrichment state; a failure after core success is a successful `partial` state with safe context.
- Empty or unavailable core profiles, access, capacity, and source failures use distinct safe caller-facing outcomes.
- The feature adds no persistence, source client, crawler, transport behavior, or change to lower-level contracts.

## Expected Red-Green-Refactor Flow

1. **Red**: Add failing unit, contract, integration, and protocol tests for validation, core profile mapping, provenance, contact safety, tri-state classification, bounded latest enrichment, safe errors, discovery, and default registration.
2. **Green**: Add only the channel-family descriptor, validator, one-channel adapter, core mapper, public-only contact and heuristic helpers, one-item uploads-playlist enrichment, safe error mapping, exports, and registration needed for those tests.
3. **Refactor**: Consolidate local channel-family helpers, retain reStructuredText docstrings on every new or changed Python function, then rerun focused and full checks.

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

- The matched seed slice, `YT-305`.
- Failing-test evidence before implementation and passing focused-test evidence after it.
- Discovery output proving `channels_getChannel` is concrete, registered by the default dispatcher, and has no representative-only marker.
- Result evidence for an available channel with a latest-video timestamp, a channel with no available latest timestamp, a public-contact normalization case, `creator`, `brand`, and `unknown` heuristic cases, an unavailable core channel, and an enrichment partial failure.
- Evidence that every invocation makes one core lookup and at most one playlist-item lookup.
- Passing full-suite and lint output.
- Confirmation that all new or changed Python functions have reStructuredText docstrings.

## Implementation Verification Evidence

Completed on 2026-08-11:

- Focused channel-detail verification: `117 passed`.
- Full repository verification: `4341 passed, 1 skipped`.
- Lint verification: `All checks passed!` from `PYTHONPATH=src python3 -m ruff check .`.

The skipped live YouTube smoke test remains credential-gated; no skipped test is associated with `channels_getChannel`.
