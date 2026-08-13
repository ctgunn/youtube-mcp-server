# Quickstart: Verify `transcripts_listLanguages`

## Prerequisites

- Python 3.11 or later and repository dependencies are installed.
- Authorized caption access is needed only for a credential-gated live check. Never place OAuth values, caption content, raw source responses, or sensitive track metadata in commands, fixtures, or logs.

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

- only a non-empty `videoId` is accepted and invalid input makes no lower-layer call;
- exactly one authorized `captions.list` request is made with the video and `snippet` part;
- every returned source track is presented separately in source order, including repeated languages;
- source identifiers and approved metadata are preserved only when supplied, with provenance; no values are invented;
- an authorized completed empty listing returns `no_accessible_languages` rather than an error;
- authorization, quota, source-unavailable, and unexpected-source outcomes remain distinct and sanitized; and
- the descriptor is concrete, registered by default, and exposes no `representativeOnly` marker.

## Review Discovery Expectations

Confirm the discovered descriptor matches [the contract](./contracts/transcripts-list-languages-contract.md): required `videoId`, one caption-list dependency, one-read/no-download bound, source metadata and provenance, empty-success behavior, OAuth/quota caveat, no selection or caption-content behavior, and safe recovery categories.

## Final Repository Evidence

Before considering the feature complete, run from `/Users/ctgunn/Projects/youtube-mcp-server`:

```bash
PYTHONPATH=src python3 -m pytest
PYTHONPATH=src python3 -m ruff check .
```

Both commands must pass after the final code and reStructuredText-docstring changes. Pull-request evidence must show Red-Green-Refactor progression and the final full-suite result.
