#!/usr/bin/env python3
"""Run a credential-gated, read-only YouTube Data API smoke check."""

from __future__ import annotations

import os
import sys
from collections.abc import Mapping
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "src"))

from mcp_server.app import create_app


def run_live_smoke(environment: Mapping[str, str] | None = None) -> dict[str, object]:
    """Call a public, read-only YouTube endpoint using configured credentials.

    :param environment: Optional environment mapping, primarily for verification tests.
    :return: Safe result summary without credential values or response content.
    :raises RuntimeError: If the explicit live-check gate or API key is missing.
    """
    values = dict(os.environ if environment is None else environment)
    if values.get("RUN_YOUTUBE_LIVE_SMOKE") != "1":
        raise RuntimeError("set RUN_YOUTUBE_LIVE_SMOKE=1 to authorize the live YouTube smoke check")
    if not values.get("YOUTUBE_API_KEY", "").strip():
        raise RuntimeError("YOUTUBE_API_KEY is required for the live YouTube smoke check")
    values.setdefault("MCP_ENVIRONMENT", "dev")

    app = create_app(env=values)
    result = app.dispatcher.call_tool("i18nLanguages_list", {"part": "snippet"})
    items = result.get("items", []) if isinstance(result, dict) else []
    return {"operation": "i18nLanguages.list", "itemCount": len(items), "status": "passed"}


def main() -> int:
    """Run the smoke check and print only its safe status summary.

    :return: Process exit code.
    """
    try:
        result = run_live_smoke()
    except Exception as error:  # noqa: BLE001 - the CLI is the final user-facing error boundary.
        print(f"YouTube live smoke check failed: {error}", file=sys.stderr)
        return 1
    print(f"YouTube live smoke check passed: {result['operation']} returned {result['itemCount']} items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
