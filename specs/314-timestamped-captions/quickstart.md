# Quickstart: Verify `transcripts_getTimestampedCaptions`

## Prerequisites

- Python 3.11 or later and repository dependencies are installed.
- Authorized caption access is needed only for a credential-gated live check. Never place OAuth values, caption text, downloaded VTT, raw source responses, or protected track metadata in commands, fixtures, or logs.

## Install

From `/Users/ctgunn/Projects/youtube-mcp-server`:

```bash
python3 -m pip install -e . ruff
```

## Verify the Public Contract and Behavior

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

- only non-empty `videoId` and an optional valid `language` are accepted, and invalid input makes no lower-layer call;
- exactly one authorized `captions.list` request is made and at most one selected-track VTT download occurs;
- explicit language selection is exact, and omitted language uses the documented source-default then source-order selection rule;
- every valid VTT cue becomes one ordered segment with non-negative elapsed start/end seconds, including hour values, adjacent/overlapping cues, and blank cue text;
- cue markup is safely removed without merging, splitting, sorting, or changing cue timing boundaries;
- a completed empty listing, explicit unavailable language, authorization, quota, endpoint-unavailable, malformed-VTT, and unexpected-source outcomes are distinct and safe; and
- the descriptor is concrete, registered by default, and exposes no `representativeOnly` marker.

## Review Discovery Expectations

Confirm the discovered descriptor matches [the contract](./contracts/transcripts-get-timestamped-captions-contract.md): required `videoId`, optional `language`, bounded authorized caption dependencies, deterministic selection, VTT timing/segment semantics, field provenance, no other-language or external fallback, OAuth/quota caveats, and safe error categories.

## Final Repository Evidence

Before considering the feature complete, run from `/Users/ctgunn/Projects/youtube-mcp-server`:

```bash
PYTHONPATH=src python3 -m pytest
PYTHONPATH=src python3 -m ruff check .
```

Both commands must pass after the final code and reStructuredText-docstring changes. Pull-request evidence must show Red-Green-Refactor progression and the final full-suite result.
