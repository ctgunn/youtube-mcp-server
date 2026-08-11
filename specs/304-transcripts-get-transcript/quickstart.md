# Quickstart: Verify `transcripts_getTranscript`

## Prerequisites

- Python 3.11 or later and repository dependencies are installed.
- An authorized caption-access configuration is available only for credential-gated live checks. Never put OAuth values, transcript contents, or raw source responses in commands, fixtures, or logs.

## Install

From `/Users/ctgunn/Projects/youtube-mcp-server`:

```bash
python3 -m pip install -e . ruff
```

## Verify the Public Contract and Behavior

After implementation, run the focused feature suite:

```bash
python3 -m pytest \
  tests/unit/test_youtube_composed_transcripts.py \
  tests/contract/test_youtube_composed_transcripts_contract.py \
  tests/integration/test_youtube_composed_tool_registration.py \
  tests/integration/test_youtube_tool_registration.py \
  tests/unit/test_runtime_config_validation.py
```

The suite must prove:

- explicit language overrides configured default, which overrides English;
- only an exact matching accessible language is selected, deterministically;
- one caption discovery call and at most one download occur;
- VTT is normalized to complete text, while an empty successful track remains distinct from unavailable;
- unavailable, authorization-sensitive, quota, malformed-content, and source-failure outcomes are distinct and safe;
- discovery is concrete rather than representative-only, and the default dispatcher registers the tool.

Verify protocol serialization after implementation:

```bash
python3 -m pytest tests/unit/test_method_routing.py
```

## Review Discovery Expectations

Confirm the discovered descriptor matches [the contract](./contracts/transcripts-get-transcript-contract.md): required `videoId`, optional `language`, exact language-selection order, authorized caption dependencies, boundedness, VTT-to-text normalization, field provenance, no fallback or translation, quota/auth caveats, and safe error categories.

## Final Repository Evidence

Before considering the feature complete, run from `/Users/ctgunn/Projects/youtube-mcp-server`:

```bash
python3 -m pytest
ruff check .
```

Both commands must pass after the final code and reStructuredText-docstring changes. Pull-request evidence must show Red-Green-Refactor progression and the final full-suite result.
