"""Red/green tests for safe public result reuse."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.config import ResultCacheSettings
from mcp_server.hardening.result_cache import ResultCache


class ResultCachePolicyTests(unittest.TestCase):
    """Verify explicit eligibility and expiry boundaries."""

    def test_fetch_is_cached_but_search_and_sensitive_variants_bypass(self) -> None:
        """Allow only documented public-safe read results to be reused."""
        now = [100.0]
        cache = ResultCache(ResultCacheSettings(), clock=lambda: now[0])

        self.assertEqual(cache.status_for("fetch", {"id": "doc-1"}), "miss")
        cache.put("fetch", {"id": "doc-1"}, {"id": "doc-1"})
        self.assertEqual(cache.get("fetch", {"id": "doc-1"}), {"id": "doc-1"})
        self.assertEqual(cache.status_for("search", {"query": "private"}), "bypass")
        self.assertEqual(cache.status_for("commentThreads_list", {"moderationStatus": "heldForReview"}), "bypass")
        now[0] += 301
        self.assertIsNone(cache.get("fetch", {"id": "doc-1"}))

    def test_related_successful_mutation_invalidates_cached_playlist_items(self) -> None:
        """Remove only mapped public read entries after a mutation succeeds."""
        cache = ResultCache(ResultCacheSettings())
        arguments = {"playlistId": "playlist-1", "part": "snippet"}
        cache.put("playlistItems_list", arguments, {"items": []})

        cache.invalidate_related("playlistItems_delete")

        self.assertIsNone(cache.get("playlistItems_list", arguments))


if __name__ == "__main__":
    unittest.main()
