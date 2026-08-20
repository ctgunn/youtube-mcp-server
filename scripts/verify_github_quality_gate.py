#!/usr/bin/env python3
"""Verify safe GitHub quality-gate evidence without changing repository settings."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

REQUIRED_CHECKS = ("lint", "typecheck", "tests")
GITHUB_ACTIONS_APP = "github-actions"


def _mapping(value: object) -> Mapping[str, Any]:
    """Return a string-keyed mapping or an empty mapping.

    :param value: Candidate decoded JSON value.
    :return: Mapping value when the input is a JSON object.
    """
    return value if isinstance(value, Mapping) else {}


def _safe_check_state(check: Mapping[str, Any], head_sha: str) -> str:
    """Classify one check result against the resolved protected revision.

    :param check: GitHub check evidence stripped of logs and credentials.
    :param head_sha: Full commit SHA that must own the result.
    :return: ``pass`` or a safe blocking state label.
    """
    if check.get("head_sha") != head_sha:
        return "stale"
    if check.get("app") != GITHUB_ACTIONS_APP:
        return "wrong_source"
    if check.get("status") != "completed":
        return "pending"
    conclusion = check.get("conclusion")
    return "pass" if conclusion == "success" else str(conclusion or "missing")


def _normalized_policy(policy: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize a GitHub ruleset response to the verifier policy shape.

    :param policy: Either normalized policy evidence or a GitHub ruleset response.
    :return: Stable policy fields used by eligibility evaluation.
    """
    if "rules" not in policy:
        return dict(policy)
    rules = [rule for raw_rule in policy.get("rules", ()) if isinstance(raw_rule, Mapping) for rule in (_mapping(raw_rule),)]
    status_rule = next((rule for rule in rules if rule.get("type") == "required_status_checks"), {})
    status_parameters = _mapping(status_rule.get("parameters"))
    required_checks = tuple(
        check.get("context")
        for raw_check in status_parameters.get("required_status_checks", ())
        if isinstance(raw_check, Mapping)
        for check in (_mapping(raw_check),)
        if isinstance(check.get("context"), str)
    )
    return {
        "enforcement": policy.get("enforcement"),
        "requires_pull_requests": any(rule.get("type") == "pull_request" for rule in rules),
        "requires_up_to_date": status_parameters.get("strict_required_status_checks_policy"),
        "bypass_actors": policy.get("bypass_actors", ()),
        "required_checks": required_checks,
    }


def evaluate_quality_gate(policy: Mapping[str, Any], check_report: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate safe policy/check evidence for a protected revision.

    :param policy: Read-only normalized active-rule evidence.
    :param check_report: Read-only check evidence for one requested revision.
    :return: Machine-readable eligibility, blocking categories, and remediation.
    """
    normalized_policy = _normalized_policy(policy)
    policy_failures: list[str] = []
    if normalized_policy.get("enforcement") != "active":
        policy_failures.append("inactive_rule")
    if normalized_policy.get("requires_pull_requests") is not True:
        policy_failures.append("pull_requests_not_required")
    if normalized_policy.get("requires_up_to_date") is not True:
        policy_failures.append("latest_revision_not_required")
    if normalized_policy.get("bypass_actors"):
        policy_failures.append("maintainer_bypass_present")
    if tuple(normalized_policy.get("required_checks", ())) != REQUIRED_CHECKS:
        policy_failures.append("required_check_set_mismatch")

    head_sha = check_report.get("head_sha")
    if not isinstance(head_sha, str) or not head_sha:
        policy_failures.append("missing_revision")
        head_sha = ""
    checks_by_name = {
        check.get("name"): check
        for raw_check in check_report.get("checks", ())
        if isinstance(raw_check, Mapping)
        for check in (_mapping(raw_check),)
        if isinstance(check.get("name"), str)
    }
    check_states = {
        name: _safe_check_state(checks_by_name[name], head_sha) if name in checks_by_name else "missing"
        for name in REQUIRED_CHECKS
    }
    blocking_checks = [name for name, state in check_states.items() if state != "pass"]
    eligible = not policy_failures and not blocking_checks
    return {
        "eligible": eligible,
        "revision": head_sha or None,
        "policyFailures": policy_failures,
        "checkStates": check_states,
        "blockingChecks": blocking_checks,
        "nextStep": "proceed_to_independent_review" if eligible else "correct_or_rerun_the_named_blocking_check",
    }


def _load_json(path: Path) -> Mapping[str, Any]:
    """Load one JSON-object evidence file.

    :param path: Read-only path to a policy or check evidence file.
    :return: Decoded JSON object.
    :raises ValueError: If the file does not contain a JSON object.
    """
    payload = json.loads(path.read_text())
    if not isinstance(payload, Mapping):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def main(argv: Sequence[str] | None = None) -> int:
    """Run the read-only policy/check verifier and emit safe JSON.

    :param argv: Optional command-line arguments for programmatic invocation.
    :return: Zero for eligible evidence and one for blocked evidence.
    :raises ValueError: If an evidence file has an invalid JSON shape.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy-file", type=Path, required=True)
    parser.add_argument("--checks-file", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = evaluate_quality_gate(_load_json(args.policy_file), _load_json(args.checks_file))
    encoded = json.dumps(result, sort_keys=True)
    if args.output is not None:
        args.output.write_text(encoded + "\n")
    else:
        print(encoded)
    return 0 if result["eligible"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
