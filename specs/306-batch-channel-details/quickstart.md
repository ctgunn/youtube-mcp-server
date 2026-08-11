# Quickstart: YT-306 Batch Channel Details

## Prerequisites

- Work from branch `306-batch-channel-details`.
- Run the local MCP service with configured public YouTube access appropriate to the existing runtime.
- Use a client that can discover and invoke MCP tools.

## Discover the Tool

Confirm discovery advertises `channels_getChannels` and documents:

- required `channelIds` list with a 1–50 limit;
- optional `parts`, defaulting to `snippet`;
- optional `includeLatestUpload`, defaulting to `true`;
- ordered `results`, summary counts, provenance, per-item outcomes, and bounded enrichment behavior.

## Invoke a Default Batch

```json
{
  "name": "channels_getChannels",
  "arguments": {
    "channelIds": ["UC111", "UC222"]
  }
}
```

Verify that the result preserves the two requested IDs in order. Each available item should include the default public profile selection, normalized metadata where available, provenance, and either a latest-upload timestamp or an explicit enrichment state.

## Request Selected Details Without Enrichment

```json
{
  "name": "channels_getChannels",
  "arguments": {
    "channelIds": ["UC111", "UC222"],
    "parts": ["contentDetails"],
    "includeLatestUpload": false
  }
}
```

Verify that every successful item reports `enrichment.status` as `not_requested`, omits `latestVideoPublishedAt`, and includes only the selected source-detail group plus identity, outcome, and provenance fields.

## Verify Mixed Outcomes

Invoke a batch with a known available ID and an inaccessible or nonexistent ID. Confirm that:

- the available channel remains a usable item;
- the other result has the generic item outcome `unavailable_resource` without the underlying availability reason; and
- summary counts partition the requested items correctly.

## Development Verification

Use Red-Green-Refactor development: first add focused failing tests, then the smallest implementation, then cleanup without behavior changes. Before review, run:

```bash
python3 -m pytest
python3 -m ruff check .
```

The feature is not complete unless both commands pass after the final code changes. Verify YT-305 regression behavior alongside the new batch tests.
