resource "google_redis_instance" "session_store" {
  name               = "${var.service_name}-${var.environment}-sessions"
  tier               = var.redis_tier
  memory_size_gb     = var.redis_memory_size_gb
  region             = var.region
  authorized_network = var.redis_authorized_network != "" ? var.redis_authorized_network : null
  redis_version      = "REDIS_7_0"
  display_name       = "${var.service_name} ${var.environment} session store"
}
