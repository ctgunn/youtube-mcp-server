locals {
  managed_network_name           = var.managed_network_name != "" ? var.managed_network_name : "${var.service_name}-${var.environment}-network"
  managed_subnet_name            = var.managed_subnet_name != "" ? var.managed_subnet_name : "${var.service_name}-${var.environment}-subnet"
  managed_direct_vpc_subnet_name = var.managed_direct_vpc_subnet_name != "" ? var.managed_direct_vpc_subnet_name : "${var.service_name}-${var.environment}-direct-egress"
  existing_secret_names          = toset(compact(split(",", lookup(data.external.secret_inventory.result, "existing_secret_names", ""))))
  missing_secret_names           = toset([for name in var.secret_names : name if !contains(local.existing_secret_names, name)])
  runtime_env = {
    MCP_ENVIRONMENT                               = var.environment
    MCP_SECRET_ACCESS_MODE                        = var.secret_access_mode
    MCP_SECRET_REFERENCE_NAMES                    = join(",", var.secret_names)
    PUBLIC_INVOCATION_INTENT                      = var.public_invocation_intent
    MCP_AUTH_REQUIRED                             = tostring(var.mcp_auth_required)
    MCP_ALLOWED_ORIGINS                           = var.mcp_allowed_origins
    MCP_ALLOW_ORIGINLESS_CLIENTS                  = tostring(var.mcp_allow_originless_clients)
    MCP_SESSION_BACKEND                           = var.session_backend
    MCP_SESSION_CONNECTIVITY_MODEL                = var.session_connectivity_model
    MCP_SESSION_DURABILITY_REQUIRED               = tostring(var.session_durability_required)
    MCP_SESSION_TTL_SECONDS                       = tostring(var.session_ttl_seconds)
    MCP_SESSION_REPLAY_TTL_SECONDS                = tostring(var.session_replay_ttl_seconds)
    MCP_RATE_LIMIT_IDENTIFIED_REQUESTS_PER_MINUTE = tostring(var.rate_limit_identified_requests_per_minute)
    MCP_RATE_LIMIT_ANONYMOUS_REQUESTS_PER_MINUTE  = tostring(var.rate_limit_anonymous_requests_per_minute)
    MCP_RATE_LIMIT_WINDOW_SECONDS                 = tostring(var.rate_limit_window_seconds)
    MCP_RATE_LIMIT_BACKEND                        = var.hardening_backend
    MCP_RESULT_CACHE_ENABLED                      = tostring(var.result_cache_enabled)
    MCP_RESULT_CACHE_BACKEND                      = var.hardening_backend
    MCP_RESULT_CACHE_MAX_FRESHNESS_SECONDS        = tostring(var.result_cache_max_freshness_seconds)
    MCP_ALERTING_ENABLED                          = tostring(var.alerting_enabled)
    MCP_ALERTING_BACKEND                          = var.hardening_backend
  }
}

data "external" "secret_inventory" {
  program = ["python3", "${path.module}/scripts/secret_inventory.py"]

  query = {
    project_id   = var.project_id
    gcloud_bin   = var.gcloud_bin
    secret_names = join(",", var.secret_names)
  }
}

resource "google_service_account" "runtime" {
  account_id   = var.service_account_name
  display_name = "${var.service_name} runtime"
}

resource "google_secret_manager_secret" "runtime" {
  for_each  = local.missing_secret_names
  secret_id = each.value

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_iam_member" "runtime_accessor" {
  for_each = toset(var.secret_names)

  secret_id = "projects/${var.project_id}/secrets/${each.value}"
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.runtime.email}"
}

resource "google_cloud_run_v2_service" "service" {
  name     = var.service_name
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account                  = google_service_account.runtime.email
    timeout                          = "${var.timeout_seconds}s"
    max_instance_request_concurrency = var.concurrency

    vpc_access {
      egress = "PRIVATE_RANGES_ONLY"

      network_interfaces {
        network    = google_compute_network.hosted.id
        subnetwork = google_compute_subnetwork.direct_vpc_egress.id
      }
    }

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

      dynamic "env" {
        for_each = toset(var.secret_names)
        content {
          name = env.value
          value_source {
            secret_key_ref {
              secret  = env.value
              version = "latest"
            }
          }
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
