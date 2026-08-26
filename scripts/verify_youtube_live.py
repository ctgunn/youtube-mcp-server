#!/usr/bin/env python3
"""Run a credential-gated, allowlisted, read-only YouTube smoke check."""

from __future__ import annotations

import os
import sys
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "src"))

from mcp_server.app import create_app

MCP_PATH = "/mcp"
MAX_LIVE_SMOKE_CASES = 12
FORBIDDEN_LIVE_SMOKE_MARKERS = (
    "_insert",
    "_update",
    "_delete",
    "_upload",
    "_download",
    "_rate",
    "_report",
    "moderation",
)


class LiveSmokeError(RuntimeError):
    """Represent a credential-safe smoke workflow failure.

    :param safe_message: Fixed operator-facing message without dynamic diagnostics.
    """

    def __init__(self, safe_message: str) -> None:
        """Store the fixed credential-safe failure message.

        :param safe_message: Approved message suitable for CLI output.
        """
        super().__init__(safe_message)
        self.safe_message = safe_message


@dataclass(frozen=True)
class LiveSmokeCase:
    """Describe one reviewed public read-only live-smoke invocation.

    :param tool_name: Explicitly approved public MCP tool name.
    :param arguments: Reviewed public object arguments.
    :param purpose: Reason the selected tool and input are safe.
    :param expected_endpoint: Upstream operation reported by a successful tool call.
    :param fixture_source_tool: Earlier approved tool that supplies a bounded public fixture.
    :param request_bound: Maximum MCP invocation count permitted for the case.
    :param timeout_seconds: Maximum configured upstream timeout allowed for the case.
    """

    tool_name: str
    arguments: Mapping[str, object]
    purpose: str
    expected_endpoint: str
    fixture_source_tool: str | None = None
    request_bound: int = 1
    timeout_seconds: float = 10.0

    def __post_init__(self) -> None:
        """Validate the explicit API-key public-read allowlist entry.

        :raises ValueError: If the entry is malformed, unsafe, or unbounded.
        """
        if not isinstance(self.tool_name, str) or not self.tool_name.strip():
            raise ValueError("live smoke tool name is required")
        normalized_name = self.tool_name.lower()
        if any(marker in normalized_name for marker in FORBIDDEN_LIVE_SMOKE_MARKERS):
            raise ValueError("live smoke tool is not an approved read-only operation")
        if not isinstance(self.arguments, Mapping):
            raise ValueError("live smoke arguments must be an object")
        if not isinstance(self.purpose, str) or not self.purpose.strip():
            raise ValueError("live smoke purpose is required")
        if not isinstance(self.expected_endpoint, str) or not self.expected_endpoint:
            raise ValueError("live smoke expected endpoint is required")
        if self.fixture_source_tool is not None and (
            not isinstance(self.fixture_source_tool, str)
            or not self.fixture_source_tool.strip()
        ):
            raise ValueError("live smoke fixture source tool must be a tool name")
        if not isinstance(self.request_bound, int) or self.request_bound < 1:
            raise ValueError("live smoke request bound must be positive")
        if (
            not isinstance(self.timeout_seconds, (float, int))
            or self.timeout_seconds <= 0
        ):
            raise ValueError("live smoke timeout must be positive")


LIVE_SMOKE_ALLOWLIST = (
    LiveSmokeCase(
        tool_name="activities_list",
        arguments={
            "part": "snippet",
            "channelId": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
            "maxResults": 1,
        },
        purpose="Public activity lookup for the documented Google Developers channel.",
        expected_endpoint="activities.list",
    ),
    LiveSmokeCase(
        tool_name="channels_list",
        arguments={"part": "snippet", "id": "UC_x5XG1OV2P6uZZ5FSM9Ttw"},
        purpose="Public channel lookup for the documented Google Developers channel.",
        expected_endpoint="channels.list",
    ),
    LiveSmokeCase(
        tool_name="channelSections_list",
        arguments={"part": "snippet", "channelId": "UC_x5XG1OV2P6uZZ5FSM9Ttw"},
        purpose="Public channel-section lookup for the documented Google Developers channel.",
        expected_endpoint="channelSections.list",
    ),
    LiveSmokeCase(
        tool_name="commentThreads_list",
        arguments={"part": "snippet", "videoId": "dQw4w9WgXcQ", "maxResults": 1},
        purpose="Public top-level comment-thread lookup for a documented public video.",
        expected_endpoint="commentThreads.list",
    ),
    LiveSmokeCase(
        tool_name="comments_list",
        arguments={"part": "snippet", "maxResults": 1},
        purpose="Public reply lookup using one comment identifier from the approved thread fixture.",
        expected_endpoint="comments.list",
        fixture_source_tool="commentThreads_list",
    ),
    LiveSmokeCase(
        tool_name="i18nLanguages_list",
        arguments={"part": "snippet"},
        purpose="Public language-reference lookup requiring API-key read capability only.",
        expected_endpoint="i18nLanguages.list",
    ),
    LiveSmokeCase(
        tool_name="i18nRegions_list",
        arguments={"part": "snippet"},
        purpose="Public content-region reference lookup requiring API-key read capability only.",
        expected_endpoint="i18nRegions.list",
    ),
    LiveSmokeCase(
        tool_name="playlistItems_list",
        arguments={
            "part": "snippet",
            "playlistId": "UU_x5XG1OV2P6uZZ5FSM9Ttw",
            "maxResults": 1,
        },
        purpose="Public uploads-playlist lookup for the documented Google Developers channel.",
        expected_endpoint="playlistItems.list",
    ),
    LiveSmokeCase(
        tool_name="playlists_list",
        arguments={
            "part": "snippet",
            "channelId": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
            "maxResults": 1,
        },
        purpose="Public playlist lookup for the documented Google Developers channel.",
        expected_endpoint="playlists.list",
    ),
    LiveSmokeCase(
        tool_name="search_list",
        arguments={"part": "snippet", "q": "Google Developers", "maxResults": 1},
        purpose="Bounded public keyword search with no owner-scoped filters.",
        expected_endpoint="search.list",
    ),
    LiveSmokeCase(
        tool_name="videoCategories_list",
        arguments={"part": "snippet", "regionCode": "US"},
        purpose="Public US video-category reference lookup.",
        expected_endpoint="videoCategories.list",
    ),
    LiveSmokeCase(
        tool_name="videos_list",
        arguments={"part": "snippet", "id": "dQw4w9WgXcQ"},
        purpose="Public video lookup for a documented public video.",
        expected_endpoint="videos.list",
    ),
)


def _require_live_smoke_authorization(values: Mapping[str, str]) -> None:
    """Fail closed before app construction when smoke prerequisites are absent.

    :param values: Candidate environment values used by the workflow.
    :return: ``None`` after validating explicit enablement and API-key presence.
    :raises LiveSmokeError: If the enablement flag or required API key is absent.
    """
    if values.get("RUN_YOUTUBE_LIVE_SMOKE") != "1":
        raise LiveSmokeError(
            "set RUN_YOUTUBE_LIVE_SMOKE=1 to authorize the live YouTube smoke check"
        )
    if not values.get("YOUTUBE_API_KEY", "").strip():
        raise LiveSmokeError(
            "YOUTUBE_API_KEY is required for the live YouTube smoke check"
        )


def _route_request(
    transport: Any, request_id: str, method: str, params: dict[str, object]
) -> dict[str, object]:
    """Send one JSON-RPC request through the public MCP route.

    :param transport: Configured in-process MCP transport.
    :param request_id: Safe unique request identifier for smoke diagnostics.
    :param method: Public MCP method name.
    :param params: Object-shaped JSON-RPC method parameters.
    :return: JSON-RPC response envelope.
    :raises LiveSmokeError: If the transport does not return an object envelope.
    """
    response = transport.handle(
        MCP_PATH,
        {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params},
    )
    if not isinstance(response, dict):
        raise LiveSmokeError(
            "live YouTube smoke check received an invalid MCP response"
        )
    return response


def _discovered_tool_names(transport: Any) -> set[str]:
    """Discover the active public MCP catalog before smoke selection.

    :param transport: Configured in-process MCP transport.
    :return: Non-empty public tool-name set from ``tools/list``.
    :raises LiveSmokeError: If discovery is unavailable or malformed.
    """
    response = _route_request(transport, "live-smoke-list", "tools/list", {})
    result = response.get("result")
    tools = result.get("tools") if isinstance(result, dict) else None
    if not isinstance(tools, list):
        raise LiveSmokeError(
            "live YouTube smoke check could not discover the MCP catalog"
        )
    names = {tool.get("name") for tool in tools if isinstance(tool, dict)}
    if not names or not all(isinstance(name, str) and name for name in names):
        raise LiveSmokeError(
            "live YouTube smoke check discovered an invalid MCP catalog"
        )
    return {str(name) for name in names}


def _validate_runtime_timeout(
    transport: Any, selected_cases: tuple[LiveSmokeCase, ...]
) -> None:
    """Ensure selected live calls retain a finite configured timeout bound.

    :param transport: Configured transport exposing optional YouTube runtime settings.
    :param selected_cases: Reviewed cases selected from current discovery.
    :return: ``None`` after confirming configured timeouts are within case bounds.
    :raises LiveSmokeError: If a configured timeout is missing or exceeds the bound.
    """
    settings = getattr(transport, "youtube_runtime_settings", None)
    configured_timeout = getattr(settings, "timeout_seconds", 10.0)
    if not isinstance(configured_timeout, (float, int)) or configured_timeout <= 0:
        raise LiveSmokeError(
            "live YouTube smoke check has an invalid configured timeout"
        )
    if any(configured_timeout > case.timeout_seconds for case in selected_cases):
        raise LiveSmokeError(
            "live YouTube smoke check exceeds its approved timeout bound"
        )


def _safe_case_result(
    case: LiveSmokeCase, response: dict[str, object]
) -> dict[str, object]:
    """Classify one MCP call without copying response or error content.

    :param case: Reviewed allowlist entry that was invoked.
    :param response: Public MCP response envelope.
    :return: Credential-safe success, availability-error, or failure summary.
    """
    error = response.get("error")
    if isinstance(error, dict):
        details = error.get("data")
        category = details.get("category") if isinstance(details, dict) else None
        return {
            "toolName": case.tool_name,
            "outcome": "safe_error",
            "category": category
            if isinstance(category, str) and category
            else "live_smoke_failure",
        }
    result = response.get("result")
    if not isinstance(result, dict) or result.get("isError") is True:
        return {
            "toolName": case.tool_name,
            "outcome": "failure",
            "category": "live_smoke_failure",
        }
    content = result.get("content")
    if not isinstance(content, list) or not content:
        return {
            "toolName": case.tool_name,
            "outcome": "failure",
            "category": "live_smoke_failure",
        }
    first_content = content[0]
    structured_content = (
        first_content.get("structuredContent")
        if isinstance(first_content, dict)
        else None
    )
    if not isinstance(structured_content, dict):
        return {
            "toolName": case.tool_name,
            "outcome": "failure",
            "category": "live_smoke_failure",
        }
    endpoint = structured_content.get("endpoint")
    items = structured_content.get("items")
    if endpoint != case.expected_endpoint:
        return {
            "toolName": case.tool_name,
            "outcome": "failure",
            "category": "unexpected_endpoint",
        }
    summary: dict[str, object] = {"toolName": case.tool_name, "outcome": "success"}
    if isinstance(endpoint, str) and endpoint:
        summary["endpoint"] = endpoint
    if isinstance(items, list):
        summary["itemCount"] = len(items)
    return summary


def _comment_parent_id_from_thread_response(response: Mapping[str, object]) -> str:
    """Extract one public top-level-comment identifier without reporting it.

    :param response: MCP response from the approved ``commentThreads_list`` case.
    :return: Valid public parent-comment identifier for one bounded reply lookup.
    :raises LiveSmokeError: If the reviewed public thread fixture has no usable comment.
    """
    result = response.get("result")
    content = result.get("content") if isinstance(result, Mapping) else None
    first_content = content[0] if isinstance(content, list) and content else None
    structured_content = (
        first_content.get("structuredContent")
        if isinstance(first_content, Mapping)
        else None
    )
    items = structured_content.get("items") if isinstance(structured_content, Mapping) else None
    first_item = items[0] if isinstance(items, list) and items else None
    snippet = first_item.get("snippet") if isinstance(first_item, Mapping) else None
    top_level_comment = (
        snippet.get("topLevelComment") if isinstance(snippet, Mapping) else None
    )
    comment_id = (
        top_level_comment.get("id")
        if isinstance(top_level_comment, Mapping)
        else None
    )
    if not isinstance(comment_id, str) or not comment_id:
        raise LiveSmokeError(
            "live YouTube smoke check could not select its approved public comment fixture"
        )
    return comment_id


def _case_arguments(
    case: LiveSmokeCase, responses: Mapping[str, Mapping[str, object]]
) -> dict[str, object]:
    """Build reviewed call arguments, including the bounded derived comment fixture.

    :param case: Explicit allowlist entry selected from the live MCP catalog.
    :param responses: Prior raw MCP responses retained only for approved fixture derivation.
    :return: Call arguments that contain only reviewed public selectors.
    :raises LiveSmokeError: If an approved fixture source is unavailable or invalid.
    """
    arguments = dict(case.arguments)
    if case.fixture_source_tool is None:
        return arguments
    source_response = responses.get(case.fixture_source_tool)
    if source_response is None:
        raise LiveSmokeError("live YouTube smoke check is missing an approved fixture source")
    if case.tool_name == "comments_list":
        arguments["parentId"] = _comment_parent_id_from_thread_response(source_response)
        return arguments
    raise LiveSmokeError("live YouTube smoke check has an unsupported fixture source")


def _safe_console_line(result: Mapping[str, object]) -> str:
    """Format one selected smoke result without exposing response content.

    :param result: Credential-safe selected-tool result from :func:`run_live_smoke`.
    :return: One operator-facing status line containing only safe evidence.
    """
    tool_name = result.get("toolName")
    outcome = result.get("outcome")
    if not isinstance(tool_name, str) or not isinstance(outcome, str):
        return "unknown tool: failure; category=live_smoke_failure"
    if outcome == "success":
        endpoint = result.get("endpoint")
        item_count = result.get("itemCount")
        fields = [f"{tool_name}: success"]
        if isinstance(endpoint, str) and endpoint:
            fields.append(f"endpoint={endpoint}")
        if isinstance(item_count, int) and item_count >= 0:
            fields.append(f"items={item_count}")
        return "; ".join(fields)
    category = result.get("category")
    safe_category = (
        category if isinstance(category, str) and category else "live_smoke_failure"
    )
    return f"{tool_name}: {outcome}; category={safe_category}"


def run_live_smoke(
    environment: Mapping[str, str] | None = None,
    *,
    app_factory: Callable[..., Any] = create_app,
) -> dict[str, object]:
    """Run explicitly authorized public-read smoke cases through the MCP route.

    :param environment: Optional environment mapping, primarily for verification tests.
    :param app_factory: Configured application factory injected by deterministic tests.
    :return: Credential-safe selected/excluded tool report with bounded request count.
    :raises LiveSmokeError: If authorization, discovery, selection, or timeout checks fail.
    """
    values = dict(os.environ if environment is None else environment)
    _require_live_smoke_authorization(values)
    values.setdefault("MCP_ENVIRONMENT", "dev")
    if len(LIVE_SMOKE_ALLOWLIST) > MAX_LIVE_SMOKE_CASES:
        raise LiveSmokeError("live YouTube smoke check exceeds its approved case bound")

    transport = app_factory(env=values)
    discovered_names = _discovered_tool_names(transport)
    selected_cases = tuple(
        case
        for case in LIVE_SMOKE_ALLOWLIST
        if case.tool_name in discovered_names
        and (
            case.fixture_source_tool is None
            or case.fixture_source_tool in discovered_names
        )
    )
    if not selected_cases:
        raise LiveSmokeError(
            "live YouTube smoke check found no approved tools in the MCP catalog"
        )
    _validate_runtime_timeout(transport, selected_cases)
    excluded_names = sorted(
        discovered_names - {case.tool_name for case in selected_cases}
    )

    selected_results: list[dict[str, object]] = []
    case_responses: dict[str, Mapping[str, object]] = {}
    request_count = 0
    for case in selected_cases:
        if request_count + case.request_bound > MAX_LIVE_SMOKE_CASES:
            raise LiveSmokeError(
                "live YouTube smoke check exceeds its approved request bound"
            )
        response = _route_request(
            transport,
            f"live-smoke-call-{case.tool_name}",
            "tools/call",
            {
                "name": case.tool_name,
                "arguments": _case_arguments(case, case_responses),
            },
        )
        request_count += case.request_bound
        case_responses[case.tool_name] = response
        selected_results.append(_safe_case_result(case, response))

    return {
        "status": "passed"
        if all(result["outcome"] == "success" for result in selected_results)
        else "completed_with_safe_errors",
        "selected": selected_results,
        "excluded": excluded_names,
        "requestCount": request_count,
        "requestLimit": MAX_LIVE_SMOKE_CASES,
    }


def main() -> int:
    """Run the smoke workflow and print only its credential-safe report summary.

    :return: Process exit code for the operator-triggered command.
    """
    try:
        report = run_live_smoke()
    except LiveSmokeError as error:
        print(f"YouTube live smoke check failed: {error.safe_message}", file=sys.stderr)
        return 1
    except Exception:  # noqa: BLE001 - this is the final credential-safe CLI boundary.
        print(
            "YouTube live smoke check failed: unexpected safe failure", file=sys.stderr
        )
        return 1
    selected = report.get("selected")
    excluded = report.get("excluded")
    status = report.get("status")
    selected_results = selected if isinstance(selected, list) else []
    excluded_names = excluded if isinstance(excluded, list) else []
    output = sys.stdout if status == "passed" else sys.stderr
    heading = "passed" if status == "passed" else "failed with safe tool outcomes"
    print(f"YouTube live smoke check {heading}:", file=output)
    for result in selected_results:
        if isinstance(result, Mapping):
            print(_safe_console_line(result), file=output)
    print(f"{len(excluded_names)} excluded tool(s)", file=output)
    return 0 if status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
