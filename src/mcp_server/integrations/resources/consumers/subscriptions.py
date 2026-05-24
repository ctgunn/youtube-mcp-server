"""Higher-layer consumer summary methods for subscriptions resources."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext


class SubscriptionsConsumerMixin:
    """Provide higher-layer summaries for subscriptions resources."""

    def fetch_subscriptions_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `subscriptions.list` wrapper result.

        :param arguments: Wrapper arguments needed to fetch subscriptions.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing selector use and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        items = result.get("items", [])
        selector_used = next(
            (
                selector
                for selector in ("channelId", "id", "mine", "myRecentSubscribers", "mySubscribers")
                if selector in arguments and arguments.get(selector) not in (None, "", False)
            ),
            None,
        )
        return {
            "subscriptionCount": len(items),
            "isEmpty": not items,
            "selectorUsed": selector_used,
            "nextPageToken": result.get("nextPageToken"),
            "authPathUsed": result.get("authPath"),
            "requestContext": result.get("requestContext"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceAuthConditionNote": self.wrapper.metadata.auth_condition_note,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def create_subscription_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `subscriptions.insert` result.

        :param arguments: Wrapper arguments needed to create a subscription.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing source contract details, required create
            inputs, and create outcome.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        body = arguments.get("body")
        body_snippet = body.get("snippet", {}) if isinstance(body, dict) else {}
        body_resource = body_snippet.get("resourceId", {}) if isinstance(body_snippet, dict) else {}
        snippet = result.get("snippet")
        snippet_resource = snippet.get("resourceId", {}) if isinstance(snippet, dict) else {}
        return {
            "subscriptionId": result.get("subscriptionId") or result.get("id"),
            "isCreated": bool(result.get("subscriptionId") or result.get("id")),
            "targetChannelId": (
                result.get("targetChannelId")
                or (snippet_resource.get("channelId") if isinstance(snippet_resource, dict) else None)
                or body_resource.get("channelId")
            ),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceRequiredFields": self.wrapper.metadata.request_shape.required_fields,
            "sourceWritablePart": arguments.get("part"),
            "sourceRequiredTargetField": "body.snippet.resourceId.channelId",
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def delete_subscription_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `subscriptions.delete` result.

        :param arguments: Wrapper arguments needed to delete a subscription.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing deleted subscription identity and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        return {
            "subscriptionId": result.get("subscriptionId"),
            "isDeleted": bool(result.get("isDeleted")),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }
