"""Activities resource-family wrappers for Layer 1 YouTube integrations."""

from mcp_server.integrations.wrappers import ActivitiesListWrapper, build_activities_list_wrapper

FAMILY_NAME = "activities"
RESOURCE_NAMES = ("activities",)
BUILDER_FUNCTIONS = {"activities.list": build_activities_list_wrapper}

__all__ = ["ActivitiesListWrapper", "BUILDER_FUNCTIONS", "FAMILY_NAME", "RESOURCE_NAMES", "build_activities_list_wrapper"]
