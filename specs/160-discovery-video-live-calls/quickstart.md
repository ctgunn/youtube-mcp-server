# Quickstart: Verify Discovery, Video, and Branding Live Calls

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
# Choose one OAuth setup when testing OAuth-required tools:
export YOUTUBE_OAUTH_TOKEN='replace-with-a-short-lived-local-secret'
# Or use all three renewable OAuth values instead of YOUTUBE_OAUTH_TOKEN:
# export YOUTUBE_OAUTH_REFRESH_TOKEN='replace-with-a-local-secret'
# export YOUTUBE_OAUTH_CLIENT_ID='replace-with-a-local-secret'
# export YOUTUBE_OAUTH_CLIENT_SECRET='replace-with-a-local-secret'
```

The API key supports public search, public subscription and video-list selectors, video abuse-reason lookup, and video-category lookup. OAuth is required for restricted search, owner-scoped subscription and video-list selectors, subscription mutations, thumbnail changes, video writes/ratings, and watermark changes. The refresh-token form obtains and caches an access token in memory; all configured values remain secrets. Never include values in fixtures, expected output, logs, screenshots, or review evidence.

## 3. Run deterministic retrofit verification first

The automated tests use a controlled opener; they must not call YouTube or need real secrets.

```bash
python3 -m pytest \
  tests/unit/test_layer1_live_runtime.py \
  tests/unit/test_youtube_transport.py \
  tests/unit/test_youtube_search.py \
  tests/unit/test_youtube_subscriptions.py \
  tests/unit/test_youtube_thumbnails.py \
  tests/unit/test_youtube_video_abuse_report_reasons.py \
  tests/unit/test_youtube_video_categories.py \
  tests/unit/test_youtube_videos.py \
  tests/unit/test_youtube_watermarks.py \
  tests/integration/test_layer1_live_runtime.py \
  tests/integration/test_youtube_tool_registration.py \
  tests/integration/test_youtube_composed_tool_registration.py \
  tests/integration/test_youtube_search_registration.py \
  tests/integration/test_youtube_subscriptions_registration.py \
  tests/integration/test_youtube_thumbnails_registration.py \
  tests/integration/test_youtube_video_abuse_report_reasons_registration.py \
  tests/integration/test_youtube_video_categories_registration.py \
  tests/integration/test_youtube_videos_registration.py \
  tests/integration/test_youtube_watermarks_registration.py
```

Expected result: all targeted tests pass; the original 16-operation regression subset proves configured runtime selection and request construction; `search_list`, `videos_list`, and `videos_getVideo` prove transport → dispatcher → descriptor → wrapper → common live-transport routing; no test prints a credential.

## 4. Confirm the controlled public flows

Use controlled openers in integration tests to verify all of the following without a network call:

1. A configured API-key `search_list` request captures `GET /youtube/v3/search` and returns a distinctive nonrepresentative result.
2. A configured API-key `videos_list` request captures `GET /youtube/v3/videos` and returns a distinctive nonrepresentative result.
3. A configured `videos_getVideo` request captures the same live video-list request and returns the existing normalized detail fields.
4. An OAuth mutation captures a bearer credential without a `key` query parameter and uses the expected JSON, raw-media, multipart, or resumable form.
5. A missing selected credential makes no opener call and returns the established safe failure.
6. HTTP, malformed-response, and timeout failures are normalized; only idempotent requests receive bounded full-jitter exponential-backoff retries; no diagnostic exposes credentials or representative data.

## 5. Run the opt-in real API smoke check

The deterministic suite never contacts Google. With a real restricted API key,
run the explicit read-only verification command:

```bash
RUN_YOUTUBE_LIVE_SMOKE=1 YOUTUBE_API_KEY='your-key' python3 scripts/verify_youtube_live.py
```

It calls only `i18nLanguages.list`, prints a safe item count, and is expected to
fail if the environment lacks a usable key, quota, API enablement, or outbound
network path. Do not use this command to test mutations or uploads.

## 6. Confirm regression compatibility

```bash
python3 -m pytest \
  tests/contract/test_layer1_videos_contract.py \
  tests/contract/test_youtube_composed_videos_contract.py \
  tests/contract/test_youtube_search_contract.py \
  tests/contract/test_youtube_subscriptions_contract.py \
  tests/contract/test_youtube_thumbnails_contract.py \
  tests/contract/test_youtube_video_abuse_report_reasons_contract.py \
  tests/contract/test_youtube_video_categories_contract.py \
  tests/contract/test_youtube_videos_contract.py \
  tests/contract/test_youtube_watermarks_contract.py
```

Expected result: public schemas, metadata, validation, result shapes, lifecycle notes, and safe errors remain compatible.

## 7. Run final required checks

```bash
python3 -m pytest
python3 -m ruff check .
```

Both commands must pass after the final implementation change. A missing credential, upstream failure, or verification failure must return the existing safe normalized failure; it must never be treated as a reason to return representative data.
