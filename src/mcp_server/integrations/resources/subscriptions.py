"""Subscriptions resource-family wrappers for Layer 1 YouTube integrations."""

from mcp_server.integrations.wrappers import (
    SubscriptionsDeleteWrapper,
    SubscriptionsInsertWrapper,
    SubscriptionsListWrapper,
    build_subscriptions_delete_wrapper,
    build_subscriptions_insert_wrapper,
    build_subscriptions_list_wrapper,
)

FAMILY_NAME = "subscriptions"
RESOURCE_NAMES = ("subscriptions",)
BUILDER_FUNCTIONS = {
    "subscriptions.list": build_subscriptions_list_wrapper,
    "subscriptions.insert": build_subscriptions_insert_wrapper,
    "subscriptions.delete": build_subscriptions_delete_wrapper,
}

__all__ = [
    "BUILDER_FUNCTIONS",
    "FAMILY_NAME",
    "RESOURCE_NAMES",
    "SubscriptionsDeleteWrapper",
    "SubscriptionsInsertWrapper",
    "SubscriptionsListWrapper",
    "build_subscriptions_delete_wrapper",
    "build_subscriptions_insert_wrapper",
    "build_subscriptions_list_wrapper",
]
