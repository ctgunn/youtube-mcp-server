locals {
  runtime_env = {
    MCP_ENVIRONMENT              = var.environment
    PUBLIC_INVOCATION_INTENT     = var.public_invocation_intent
    MCP_AUTH_REQUIRED            = tostring(var.mcp_auth_required)
    MCP_ALLOWED_ORIGINS          = var.mcp_allowed_origins
    MCP_ALLOW_ORIGINLESS_CLIENTS = tostring(var.mcp_allow_originless_clients)
    MCP_SESSION_BACKEND          = var.session_backend
    MCP_SESSION_DURABILITY_REQUIRED = tostring(var.session_durability_required)
    MCP_SESSION_TTL_SECONDS         = tostring(var.session_ttl_seconds)
    MCP_SESSION_REPLAY_TTL_SECONDS  = tostring(var.session_replay_ttl_seconds)
  }
}

resource "google_service_account" "runtime" {
  account_id   = var.service_account_name
  display_name = "${var.service_name} runtime"
}

resource "google_secret_manager_secret" "runtime" {
  for_each  = toset(var.secret_names)
  secret_id = each.value

  replication {
    auto {}
  }
}

resource "google_cloud_run_v2_service" "service" {
  name     = var.service_name
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.runtime.email
    timeout         = "${var.timeout_seconds}s"
    max_instance_request_concurrency = var.concurrency

    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    containers {
      image = var.bootstrap_image_reference

      dynamic "env" {
        for_each = local.runtime_env
        content {
          name  = env.key
          value = env.value
        }
      }
    }
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
}

resource "google_cloud_run_service_iam_member" "public_invoker" {
  count = var.public_invocation_intent == "public_remote_mcp" ? 1 : 0

  location = google_cloud_run_v2_service.service.location
  service  = google_cloud_run_v2_service.service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
