output "project_id" {
  description = "Project ID consumed by the application deployment workflow."
  value       = var.project_id
}

output "region" {
  description = "Region consumed by the application deployment workflow."
  value       = var.region
}

output "environment" {
  description = "Runtime environment profile."
  value       = var.environment
}

output "service_name" {
  description = "Cloud Run service name consumed by deployment."
  value       = google_cloud_run_v2_service.service.name
}

output "service_account_email" {
  description = "Runtime identity consumed by deployment."
  value       = google_service_account.runtime.email
}

output "public_invocation_intent" {
  description = "Whether the service is intended for trusted public remote MCP access."
  value       = var.public_invocation_intent
}

output "secret_reference_names" {
  description = "Secret references passed to scripts/deploy_cloud_run.sh."
  value       = var.secret_names
}

output "mcp_secret_access_mode" {
  description = "How Cloud Run receives secret-backed runtime configuration."
  value       = var.secret_access_mode
}

output "mcp_secret_reference_names" {
  description = "Runtime secret reference names exposed to the hosted deployment workflow."
  value       = var.secret_names
}

output "mcp_auth_required" {
  description = "Hosted auth requirement."
  value       = var.mcp_auth_required
}

output "mcp_allowed_origins" {
  description = "Allowed browser origins."
  value       = var.mcp_allowed_origins
}

output "mcp_allow_originless_clients" {
  description = "Whether originless clients are allowed."
  value       = var.mcp_allow_originless_clients
}

output "mcp_session_backend" {
  description = "Hosted durable session backend."
  value       = var.session_backend
}

output "mcp_session_store_url" {
  description = "Redis URL consumed by the runtime."
  value       = "redis://${google_redis_instance.session_store.host}:6379/0"
  sensitive   = true
}

output "mcp_session_connectivity_model" {
  description = "Provider-specific model used for Cloud Run to reach the durable session backend."
  value       = var.session_connectivity_model
}

output "mcp_session_network_reference" {
  description = "Terraform-managed network reference used by the hosted durable-session path."
  value       = google_compute_network.hosted.id
}

output "mcp_session_subnet_reference" {
  description = "Terraform-managed Direct VPC egress subnet reference used by the hosted durable-session path."
  value       = google_compute_subnetwork.direct_vpc_egress.id
}

output "mcp_session_egress_reference" {
  description = "Terraform-managed Direct VPC egress resource reference for the durable-session path."
  value       = google_compute_subnetwork.direct_vpc_egress.id
}

output "mcp_session_durability_required" {
  description = "Readiness requirement for session durability."
  value       = var.session_durability_required
}

output "mcp_session_ttl_seconds" {
  description = "Inactive session TTL."
  value       = var.session_ttl_seconds
}

output "mcp_session_replay_ttl_seconds" {
  description = "Replay retention TTL."
  value       = var.session_replay_ttl_seconds
}

output "mcp_rate_limit_identified_requests_per_minute" {
  description = "Hosted identified-caller admission limit."
  value       = var.rate_limit_identified_requests_per_minute
}

output "mcp_rate_limit_anonymous_requests_per_minute" {
  description = "Hosted anonymous admission limit."
  value       = var.rate_limit_anonymous_requests_per_minute
}

output "mcp_rate_limit_window_seconds" {
  description = "Hosted admission window."
  value       = var.rate_limit_window_seconds
}

output "mcp_result_cache_enabled" {
  description = "Whether public result reuse is enabled."
  value       = var.result_cache_enabled
}

output "mcp_result_cache_max_freshness_seconds" {
  description = "Maximum public result reuse lifetime."
  value       = var.result_cache_max_freshness_seconds
}

output "mcp_alerting_enabled" {
  description = "Whether bounded alert state is enabled."
  value       = var.alerting_enabled
}

output "mcp_hardening_alert_policy_ids" {
  description = "Monitoring policy identifiers for bounded MCP incident alerts."
  value       = google_monitoring_alert_policy.mcp_hardening_incident[*].name
}

output "min_instances" {
  description = "Minimum instance count."
  value       = var.min_instances
}

output "max_instances" {
  description = "Maximum instance count."
  value       = var.max_instances
}

output "concurrency" {
  description = "Cloud Run request concurrency."
  value       = var.concurrency
}

output "timeout_seconds" {
  description = "Cloud Run request timeout."
  value       = var.timeout_seconds
}
