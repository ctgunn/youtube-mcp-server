# Quickstart: Verify Catalog, Membership, and Playlist Live Calls

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

The API key supports guide-category, localization, and public playlist-item/list paths. OAuth is required for members, membership levels, playlist images, all playlist mutations, playlist-item mutations, and owner-scoped playlist listing. Never include either value in fixtures, expected output, logs, screenshots, or review evidence.

## 3. Run deterministic retrofit verification first

The automated tests use a controlled opener; they must not call YouTube or need real secrets.

```bash
python3 -m pytest \
  tests/unit/test_layer1_live_runtime.py \
  tests/unit/test_youtube_transport.py \
  tests/unit/test_youtube_guide_categories.py \
  tests/unit/test_youtube_i18n_languages.py \
  tests/unit/test_youtube_i18n_regions.py \
  tests/unit/test_youtube_members.py \
  tests/unit/test_youtube_memberships_levels.py \
  tests/unit/test_youtube_playlist_images.py \
  tests/unit/test_youtube_playlist_items.py \
  tests/unit/test_youtube_playlists.py \
  tests/integration/test_layer1_live_runtime.py \
  tests/integration/test_youtube_tool_registration.py \
  tests/integration/test_youtube_guide_categories_registration.py \
  tests/integration/test_youtube_i18n_languages_registration.py \
  tests/integration/test_youtube_i18n_regions_registration.py \
  tests/integration/test_youtube_members_registration.py \
  tests/integration/test_youtube_memberships_levels_registration.py \
  tests/integration/test_youtube_playlist_images_registration.py \
  tests/integration/test_youtube_playlist_items_registration.py \
  tests/integration/test_youtube_playlists_registration.py
```

Expected result: all targeted tests pass; all 17 operations prove configured runtime selection and request construction; seven public-tool flows prove transport → dispatcher → descriptor → wrapper → live transport routing; no test prints a credential.

## 4. Confirm regression compatibility

```bash
python3 -m pytest \
  tests/contract/test_layer1_localization_contract.py \
  tests/contract/test_layer1_members_contract.py \
  tests/contract/test_layer1_memberships_levels_contract.py \
  tests/contract/test_layer1_playlist_images_contract.py \
  tests/contract/test_layer1_playlist_items_contract.py \
  tests/contract/test_layer1_playlists_contract.py \
  tests/contract/test_youtube_guide_categories_contract.py \
  tests/contract/test_youtube_i18n_languages_contract.py \
  tests/contract/test_youtube_i18n_regions_contract.py \
  tests/contract/test_youtube_members_contract.py \
  tests/contract/test_youtube_memberships_levels_contract.py \
  tests/contract/test_youtube_playlist_images_contract.py \
  tests/contract/test_youtube_playlist_items_contract.py \
  tests/contract/test_youtube_playlists_contract.py
```

Expected result: public schemas, metadata, validation, result shapes, lifecycle notes, and safe errors remain compatible.

## 5. Run final required checks

```bash
python3 -m pytest
python3 -m ruff check .
```

Both commands must pass after the final implementation change. A missing credential, upstream failure, or verification failure must return the existing safe normalized failure; it must never be treated as a reason to return representative data.
