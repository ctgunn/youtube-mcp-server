# Quickstart: Verify Channel and Community Live Calls

## 1. Prepare a local environment

From `/Users/ctgunn/Projects/youtube-mcp-server`:

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e .
```

Use `.env.local` or another local environment mechanism. Do not commit credentials.

## 2. Configure only the access needed for a manual live verification

```bash
export MCP_ENVIRONMENT=dev
export YOUTUBE_API_KEY='replace-with-a-local-secret'
export YOUTUBE_OAUTH_TOKEN='replace-with-a-local-secret'
```

The API key supports the eligible public read paths. OAuth is needed for owner-scoped selectors and all in-scope mutations/media operations. Never include either value in fixtures, expected output, logs, screenshots, or review evidence.

## 3. Run deterministic retrofit verification first

The automated tests use a controlled opener; they must not call YouTube or need real secrets.

```bash
python3 -m pytest \
  tests/unit/test_layer1_live_runtime.py \
  tests/unit/test_youtube_transport.py \
  tests/unit/test_youtube_activities.py \
  tests/unit/test_youtube_captions.py \
  tests/unit/test_youtube_channel_banners.py \
  tests/unit/test_youtube_channels.py \
  tests/unit/test_youtube_channel_sections.py \
  tests/unit/test_youtube_comments.py \
  tests/unit/test_youtube_comment_threads.py \
  tests/integration/test_layer1_live_runtime.py \
  tests/integration/test_youtube_activities_registration.py \
  tests/integration/test_youtube_captions_registration.py \
  tests/integration/test_youtube_channel_banners_registration.py \
  tests/integration/test_youtube_channels_registration.py \
  tests/integration/test_youtube_channel_sections_registration.py \
  tests/integration/test_youtube_comments_registration.py \
  tests/integration/test_youtube_comment_threads_registration.py
```

Expected result: all targeted tests pass; all 20 in-scope operations prove configured runtime selection and request construction; seven public-tool flows prove transport → dispatcher → descriptor → wrapper → live transport routing; no test prints a credential.

## 4. Confirm regression compatibility

```bash
python3 -m pytest \
  tests/contract/test_layer1_activities_contract.py \
  tests/contract/test_layer1_captions_contract.py \
  tests/contract/test_layer1_channel_banners_contract.py \
  tests/contract/test_layer1_channels_contract.py \
  tests/contract/test_layer1_channel_sections_contract.py \
  tests/contract/test_layer1_comments_contract.py \
  tests/contract/test_youtube_activities_contract.py \
  tests/contract/test_youtube_captions_contract.py \
  tests/contract/test_youtube_channel_banners_contract.py \
  tests/contract/test_youtube_channels_contract.py \
  tests/contract/test_youtube_channel_sections_contract.py \
  tests/contract/test_youtube_comments_contract.py
```

Expected result: public schemas, metadata, validation, result shapes, and safe errors remain compatible.

## 5. Run final required checks

```bash
python3 -m pytest
python3 -m ruff check .
```

Both commands must pass after the final implementation change. A missing credential, upstream failure, or verification failure must return the existing safe normalized failure; it must never be treated as a reason to return representative data.
