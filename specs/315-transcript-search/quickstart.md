# Quickstart: Verify `transcripts_searchTranscript`

## Prerequisites

- Python 3.11 or later and repository dependencies are installed.
- Authorized caption access is needed only for credential-gated live checks. Never place OAuth values, video IDs, query text, caption content, snippets, or raw source responses in fixtures or logs.

## Install

From `/Users/ctgunn/Projects/youtube-mcp-server`:

```bash
python3 -m pip install -e . ruff
```

## Verify Contract and Behavior

After implementation, run the focused feature suite:

```bash
PYTHONPATH=src python3 -m pytest \
  tests/unit/test_youtube_composed_transcripts.py \
  tests/contract/test_youtube_composed_transcripts_contract.py \
  tests/integration/test_youtube_composed_tool_registration.py \
  tests/integration/test_youtube_tool_registration.py \
  tests/unit/test_method_routing.py
```

The suite must prove:

- required and optional inputs, blank values, unknown fields, and the 1–50 match bound are validated before retrieval;
- the default limit is 10; matching is case-insensitive, literal, and contained in one segment;
- snippets contain only matching-segment context and timing comes from that segment;
- results are chronological before truncation, including stable ties;
- explicit language passes to exact timed retrieval with no fallback;
- successful no-match responses are distinct from no accessible captions and all safe failure categories;
- the concrete descriptor has no `representativeOnly` marker and is registered in the default tool catalog.

## Review Discovery Expectations

Confirm the discovered descriptor matches [the contract](./contracts/transcripts-search-transcript-contract.md): required `videoId` and `query`, optional `language` and `maxMatches`, timestamped retrieval plus local literal search, one-video boundedness, exact language behavior, 160-character maximum snippet rule, chronological ranking, provenance, `no_matches`, and safe error categories.

## Final Repository Evidence

Before considering the feature complete, run from `/Users/ctgunn/Projects/youtube-mcp-server`:

```bash
PYTHONPATH=src python3 -m pytest
PYTHONPATH=src python3 -m ruff check .
```

Both commands must pass after the final code and reStructuredText-docstring changes. Pull-request evidence must show Red-Green-Refactor progression and the final full-suite result.
