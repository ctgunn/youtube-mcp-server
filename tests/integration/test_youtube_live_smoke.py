"""Opt-in real YouTube Data API smoke test.

This check deliberately remains disabled unless an operator supplies a real
credential and explicitly enables it. It performs no mutation.
"""

from __future__ import annotations

import os

import pytest

import scripts.verify_youtube_live as live_smoke_module
from scripts.verify_youtube_live import LIVE_SMOKE_ALLOWLIST, run_live_smoke


def test_live_smoke_allowlist_contains_only_reviewed_api_key_public_reads() -> None:
    """Keep the live matrix limited to the reviewed API-key public-read tools.

    :return: ``None`` after preventing deprecated, OAuth-only, and mutation tools.
    """
    assert [case.tool_name for case in LIVE_SMOKE_ALLOWLIST] == [
        "activities_list",
        "channels_list",
        "channelSections_list",
        "commentThreads_list",
        "comments_list",
        "i18nLanguages_list",
        "i18nRegions_list",
        "playlistItems_list",
        "playlists_list",
        "search_list",
        "videoCategories_list",
        "videos_list",
    ]
    assert len(LIVE_SMOKE_ALLOWLIST) == live_smoke_module.MAX_LIVE_SMOKE_CASES


class _FakeSmokeTransport:
    """Record public MCP requests for deterministic live-smoke verification.

    :param call_response: Optional JSON-RPC response returned for selected tool calls.
    :param tool_names: Names exposed by deterministic catalog discovery.
    """

    def __init__(
        self,
        call_response: dict[str, object] | None = None,
        tool_names: tuple[str, ...] | None = None,
    ) -> None:
        """Initialize the route recorder with an optional safe call response.

        :param call_response: Optional fixed JSON-RPC envelope for ``tools/call``.
        :param tool_names: Tool names returned by the deterministic ``tools/list`` call.
        """
        self.requests: list[dict[str, object]] = []
        self.call_response = call_response
        self.tool_names = tool_names or tuple(
            case.tool_name for case in LIVE_SMOKE_ALLOWLIST
        )

    def handle(self, path: str, payload: dict[str, object]) -> dict[str, object]:
        """Record a public MCP request and return a deterministic envelope.

        :param path: Requested public route.
        :param payload: JSON-RPC request body.
        :return: Controlled discovery or invocation response envelope.
        """
        self.requests.append({"path": path, "payload": payload})
        if payload["method"] == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": payload["id"],
                "result": {
                    "tools": [
                        *({"name": tool_name} for tool_name in self.tool_names),
                        {"name": "videos_delete"},
                    ]
                },
            }
        if self.call_response is not None:
            return self.call_response
        tool_name = payload["params"]["name"]
        case = next(case for case in LIVE_SMOKE_ALLOWLIST if case.tool_name == tool_name)
        structured_content: dict[str, object] = {
            "endpoint": case.expected_endpoint,
            "items": [{"id": "fixture-item"}],
        }
        if tool_name == "commentThreads_list":
            structured_content["items"] = [
                {"snippet": {"topLevelComment": {"id": "public-comment-fixture"}}}
            ]
        return {
            "jsonrpc": "2.0",
            "id": payload["id"],
            "result": {
                "isError": False,
                "content": [{"structuredContent": structured_content}],
            },
        }


def test_live_smoke_fails_closed_before_app_construction() -> None:
    """Require absent authorization or credentials to prevent app construction.

    :return: ``None`` after proving both prerequisites fail closed.
    """
    called = False

    def app_factory(**_kwargs: object) -> _FakeSmokeTransport:
        """Record an unexpected attempt to construct a configured app.

        :param _kwargs: Candidate application construction keyword arguments.
        :return: A deterministic transport when unexpectedly invoked.
        """
        nonlocal called
        called = True
        return _FakeSmokeTransport()

    with pytest.raises(RuntimeError, match="RUN_YOUTUBE_LIVE_SMOKE"):
        run_live_smoke({"YOUTUBE_API_KEY": "secret"}, app_factory=app_factory)
    with pytest.raises(RuntimeError, match="YOUTUBE_API_KEY"):
        run_live_smoke({"RUN_YOUTUBE_LIVE_SMOKE": "1"}, app_factory=app_factory)
    assert called is False


def test_live_smoke_uses_only_allowlisted_public_mcp_calls() -> None:
    """Require discovery, exclusion reporting, and allowlisted MCP invocation.

    :return: ``None`` after validating the selected and excluded tool report.
    """
    transport = _FakeSmokeTransport()
    report = run_live_smoke(
        {"RUN_YOUTUBE_LIVE_SMOKE": "1", "YOUTUBE_API_KEY": "secret"},
        app_factory=lambda **_kwargs: transport,
    )
    methods = [request["payload"]["method"] for request in transport.requests]
    call_names = [
        request["payload"]["params"]["name"]
        for request in transport.requests
        if request["payload"]["method"] == "tools/call"
    ]
    assert methods == ["tools/list", *("tools/call" for _case in LIVE_SMOKE_ALLOWLIST)]
    assert call_names == [case.tool_name for case in LIVE_SMOKE_ALLOWLIST]
    assert [result["toolName"] for result in report["selected"]] == call_names
    assert [result["endpoint"] for result in report["selected"]] == [
        case.expected_endpoint for case in LIVE_SMOKE_ALLOWLIST
    ]
    comments_request = next(
        request for request in transport.requests
        if request["payload"]["params"].get("name") == "comments_list"
    )
    assert comments_request["payload"]["params"]["arguments"] == {
        "part": "snippet",
        "maxResults": 1,
        "parentId": "public-comment-fixture",
    }
    assert "videos_delete" in report["excluded"]
    assert report["requestCount"] == len(LIVE_SMOKE_ALLOWLIST)
    assert report["requestLimit"] >= report["requestCount"]


def test_live_smoke_redacts_upstream_error_content() -> None:
    """Require a safe failure category without raw upstream error text.

    :return: ``None`` after confirming sensitive error content is omitted.
    """
    transport = _FakeSmokeTransport(
        {
            "jsonrpc": "2.0",
            "id": "call",
            "error": {
                "code": -32000,
                "message": "secret-token must not be printed",
                "data": {
                    "category": "upstream_failure",
                    "authorization": "secret-token",
                },
            },
        },
        tool_names=(LIVE_SMOKE_ALLOWLIST[0].tool_name,),
    )
    report = run_live_smoke(
        {"RUN_YOUTUBE_LIVE_SMOKE": "1", "YOUTUBE_API_KEY": "secret"},
        app_factory=lambda **_kwargs: transport,
    )
    assert report["selected"][0]["outcome"] == "safe_error"
    assert report["selected"][0]["category"] == "upstream_failure"
    assert "secret-token" not in repr(report)


def test_main_reports_per_tool_live_evidence_and_rejects_safe_error_reports(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Require CLI output to show safe success evidence instead of only counts.

    :param monkeypatch: Pytest patch manager used to replace live execution.
    :param capsys: Pytest output capture fixture used to inspect CLI reporting.
    :return: ``None`` after validating safe success and failure CLI exit behavior.
    """
    success_report = {
        "status": "passed",
        "selected": [
            {
                "toolName": "i18nLanguages_list",
                "outcome": "success",
                "endpoint": "i18nLanguages.list",
                "itemCount": 2,
            }
        ],
        "excluded": ["videos_delete"],
        "requestCount": 1,
        "requestLimit": 5,
    }

    def return_success() -> dict[str, object]:
        """Return a deterministic credential-safe successful smoke report.

        :return: Selected-tool success report with only safe evidence.
        """
        return success_report

    monkeypatch.setattr(live_smoke_module, "run_live_smoke", return_success)
    assert live_smoke_module.main() == 0
    success_output = capsys.readouterr().out
    assert (
        "i18nLanguages_list: success; endpoint=i18nLanguages.list; items=2"
        in success_output
    )
    assert "1 excluded" in success_output

    def return_safe_error() -> dict[str, object]:
        """Return a deterministic credential-safe unavailable smoke report.

        :return: Selected-tool safe-error report without raw upstream details.
        """
        return {
            "status": "completed_with_safe_errors",
            "selected": [
                {
                    "toolName": "i18nLanguages_list",
                    "outcome": "safe_error",
                    "category": "upstream_failure",
                }
            ],
            "excluded": [],
            "requestCount": 1,
            "requestLimit": 5,
        }

    monkeypatch.setattr(live_smoke_module, "run_live_smoke", return_safe_error)
    assert live_smoke_module.main() == 1
    assert (
        "i18nLanguages_list: safe_error; category=upstream_failure"
        in capsys.readouterr().err
    )


@pytest.mark.skipif(
    os.environ.get("RUN_YOUTUBE_LIVE_SMOKE") != "1",
    reason="set RUN_YOUTUBE_LIVE_SMOKE=1 with a real API key to run live YouTube verification",
)
def test_i18n_languages_uses_the_live_youtube_data_api() -> None:
    """Call a public read-only endpoint with the operator-provided API key."""
    if not os.environ.get("YOUTUBE_API_KEY", "").strip():
        pytest.fail("YOUTUBE_API_KEY is required when RUN_YOUTUBE_LIVE_SMOKE=1")

    report = run_live_smoke(
        {**os.environ, "MCP_ENVIRONMENT": os.environ.get("MCP_ENVIRONMENT", "dev")}
    )

    assert report["status"] == "passed"
    assert report["selected"]
