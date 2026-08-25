"""Provide conservative in-memory public result reuse."""

from __future__ import annotations

import json
from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256
from time import time
from typing import Any

from mcp_server.config import ResultCacheSettings

_ELIGIBLE_TTLS = {
    "fetch": 300,
    "i18nlanguages_list": 300,
    "i18nregions_list": 300,
    "guidecategories_list": 300,
    "videocategories_list": 300,
    "videoabusereportreasons_list": 300,
    "playlistitems_list": 60,
    "commentthreads_list": 30,
}


@dataclass(frozen=True)
class CacheEntry:
    """Represent one complete reusable result.

    :param result: Complete successful result retained for reuse.
    :param expires_at: Monotonic wall-clock expiry point.
    """

    result: Any
    expires_at: float


class ResultCache:
    """Reuse only explicitly eligible complete public results."""

    def __init__(self, settings: ResultCacheSettings, clock: Callable[[], float] = time) -> None:
        """Initialize the local cache for a validated policy.

        :param settings: Result-reuse policy settings.
        :param clock: Injectable time source for deterministic tests.
        """
        self._settings = settings
        self._clock = clock
        self._entries: dict[str, CacheEntry] = {}

    def status_for(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """Classify whether one call can safely use the cache.

        :param tool_name: Public tool being invoked.
        :param arguments: Validated public arguments.
        :return: ``hit``, ``miss``, or ``bypass``.
        """
        if not self._eligible(tool_name, arguments):
            return "bypass"
        return "hit" if self.get(tool_name, arguments) is not None else "miss"

    def get(self, tool_name: str, arguments: dict[str, Any]) -> Any | None:
        """Return a fresh copy of a matching eligible result when available.

        :param tool_name: Public tool name.
        :param arguments: Validated public arguments.
        :return: Reusable result or ``None`` when missing, expired, or ineligible.
        """
        if not self._eligible(tool_name, arguments):
            return None
        key = self._key(tool_name, arguments)
        entry = self._entries.get(key)
        if entry is None or entry.expires_at <= self._clock():
            self._entries.pop(key, None)
            return None
        return deepcopy(entry.result)

    def put(self, tool_name: str, arguments: dict[str, Any], result: Any) -> None:
        """Store one complete successful eligible result.

        :param tool_name: Public tool name.
        :param arguments: Validated public arguments.
        :param result: Complete successful dispatcher result.
        :return: ``None`` when the result is retained or bypassed.
        """
        if not self._eligible(tool_name, arguments):
            return
        ttl = min(_ELIGIBLE_TTLS[tool_name.strip().lower()], self._settings.max_freshness_seconds)
        self._entries[self._key(tool_name, arguments)] = CacheEntry(deepcopy(result), self._clock() + ttl)

    def invalidate_related(self, tool_name: str) -> None:
        """Remove reusable entries related to one successful mutation.

        :param tool_name: Mutation tool that completed successfully.
        :return: ``None`` after the small explicit relation map is applied.
        """
        normalized = tool_name.strip().lower()
        related = "playlistitems_list" if normalized.startswith("playlistitems_") else "commentthreads_list" if normalized.startswith(("comments_", "commentthreads_")) else None
        if related is None:
            return
        for key in tuple(self._entries):
            if f":{related}:" in key:
                self._entries.pop(key, None)

    def _eligible(self, tool_name: str, arguments: dict[str, Any]) -> bool:
        """Return whether a tool/argument variant is explicitly public-safe.

        :param tool_name: Public tool name.
        :param arguments: Validated arguments to inspect.
        :return: ``True`` only for the initial conservative allowlist.
        """
        normalized = tool_name.strip().lower()
        if not self._settings.enabled or normalized not in _ELIGIBLE_TTLS:
            return False
        return not (normalized == "commentthreads_list" and arguments.get("moderationStatus") is not None)

    def _key(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """Create a stable non-secret key for validated public arguments.

        :param tool_name: Public tool name.
        :param arguments: Canonicalizable validated public arguments.
        :return: Namespaced digest suitable only for internal lookup.
        """
        canonical = json.dumps(arguments, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        digest = sha256(canonical.encode("utf-8")).hexdigest()
        return f"mcp:result-cache:{self._settings.policy_version}:{tool_name.strip().lower()}:{digest}"
