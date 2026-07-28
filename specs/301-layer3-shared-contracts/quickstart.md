# Quickstart: YT-301 Layer 3 Shared Scaffolding and Contracts

## Goal

Use this guide to validate that YT-301 planning is ready for task generation and later implementation. This slice defines shared Layer 3 contracts and scaffolding only; it must not implement concrete public tools such as `videos_getVideo` or `channels_searchChannels`.

## Read the Artifacts

1. Review the feature spec:

   ```bash
   sed -n '1,240p' /Users/ctgunn/Projects/youtube-mcp-server/specs/301-layer3-shared-contracts/spec.md
   ```

2. Review the implementation plan:

   ```bash
   sed -n '1,280p' /Users/ctgunn/Projects/youtube-mcp-server/specs/301-layer3-shared-contracts/plan.md
   ```

3. Review the research decisions:

   ```bash
   sed -n '1,240p' /Users/ctgunn/Projects/youtube-mcp-server/specs/301-layer3-shared-contracts/research.md
   ```

4. Review the contracts:

   ```bash
   sed -n '1,260p' /Users/ctgunn/Projects/youtube-mcp-server/specs/301-layer3-shared-contracts/contracts/layer3-public-tool-contract.md
   sed -n '1,260p' /Users/ctgunn/Projects/youtube-mcp-server/specs/301-layer3-shared-contracts/contracts/layer3-scaffolding-contract.md
   ```

## Planning Validation

Confirm the plan satisfies these conditions before running `/speckit.tasks`:

- All 19 initial Layer 3 tool names map to one of `videos_*`, `channels_*`, `playlists_*`, or `transcripts_*`.
- Shared repeated parameters define requiredness, defaults, bounds, validation behavior, and applicability before later tool slices use them.
- Representative response fields can be categorized as raw upstream, normalized, or heuristic/inferred.
- Heuristic fields include basis and limitation notes.
- Composite and fan-out behaviors disclose auth, quota, boundedness, and partial-result policy.
- Videos, channels, playlists, and transcripts each have a family placement rule.
- No concrete public Layer 3 tool behavior is introduced by YT-301.
- Any planned Python functions include reStructuredText docstring expectations.

## Expected Red-Green-Refactor Flow

Implementation tasks generated later should follow this order:

1. Red: add failing contract and unit tests for missing grouped names, repeated-parameter conventions, response provenance, heuristic disclosures, composition boundaries, and family layout.
2. Green: add the smallest shared Layer 3 records, validators, conventions, family maps, and representative examples needed to pass those tests.
3. Refactor: remove duplicated convention wording, keep family modules cohesive, preserve safe metadata, confirm docstrings, and rerun focused checks.

## Targeted Checks for Later Implementation

Planned focused checks:

```bash
python3 -m pytest tests/unit/test_layer3_shared_scaffolding.py tests/contract/test_layer3_shared_contract.py tests/contract/test_layer3_tool_catalog_contract.py tests/integration/test_layer3_tool_registration.py
```

Full validation after the final code change:

```bash
python3 -m pytest
python3 -m ruff check .
```

## Review Evidence

Pull request review for the later implementation should include:

- Matched seed slice: `YT-301`
- List of shared Layer 3 contract areas covered
- Representative examples from videos, channels, playlists, and transcripts
- Focused test command output
- Full `python3 -m pytest` output
- `python3 -m ruff check .` output
- Confirmation that every new or changed Python function has a reStructuredText docstring
- Confirmation that no concrete YT-302+ public tool behavior was added in this slice
