#!/usr/bin/env python3
"""Report which requested Secret Manager secrets already exist."""

from __future__ import annotations

import json
import subprocess
import sys


def _secret_exists(*, gcloud_bin: str, project_id: str, secret_name: str) -> bool:
    """Return whether the named secret already exists in the target project."""
    command = [
        gcloud_bin,
        "secrets",
        "describe",
        secret_name,
        "--project",
        project_id,
        "--format=value(name)",
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    return result.returncode == 0


def main() -> int:
    """Read Terraform external input and emit a comma-separated existence list."""
    payload = json.load(sys.stdin)
    project_id = str(payload.get("project_id", "")).strip()
    gcloud_bin = str(payload.get("gcloud_bin", "gcloud")).strip() or "gcloud"
    secret_names = [
        item.strip()
        for item in str(payload.get("secret_names", "")).split(",")
        if item.strip()
    ]
    existing = [
        secret_name
        for secret_name in secret_names
        if _secret_exists(gcloud_bin=gcloud_bin, project_id=project_id, secret_name=secret_name)
    ]
    json.dump({"existing_secret_names": ",".join(existing)}, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
