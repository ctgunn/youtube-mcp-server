variable "project_id" {
  description = "GCP project that hosts the MCP platform."
  type        = string
}

variable "region" {
  description = "Primary GCP region for the hosted MCP platform."
  type        = string
}

variable "environment" {
  description = "Deployment profile for the hosted platform."
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be one of dev, staging, or prod."
  }
}

variable "service_name" {
  description = "Cloud Run service name."
  type        = string
}

variable "service_account_name" {
  description = "Service account name to create for the hosted runtime."
  type        = string
  default     = "youtube-mcp-server"
}

variable "public_invocation_intent" {
  description = "Whether the hosted Cloud Run service is intended for trusted public remote MCP access."
  type        = string
  default     = "private_only"

  validation {
    condition     = contains(["public_remote_mcp", "private_only"], var.public_invocation_intent)
    error_message = "public_invocation_intent must be public_remote_mcp or private_only."
  }
}

variable "bootstrap_image_reference" {
  description = "Placeholder image used to create the Cloud Run service foundation before application deployment."
  type        = string
  default     = "us-docker.pkg.dev/cloudrun/container/hello"
}

variable "gcloud_bin" {
  description = "gcloud executable used by Terraform helper scripts when reconciling pre-existing GCP resources."
  type        = string
  default     = "gcloud"
}

variable "secret_access_mode" {
  description = "How Cloud Run receives required secret-backed runtime values."
  type        = string
  default     = "secret_manager_env"
}

variable "min_instances" {
  description = "Minimum instance count for the hosted runtime."
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum instance count for the hosted runtime."
  type        = number
  default     = 2
}

variable "concurrency" {
  description = "Maximum concurrent requests per Cloud Run instance."
  type        = number
  default     = 20
}

variable "timeout_seconds" {
  description = "Request timeout for the hosted runtime."
  type        = number
  default     = 180
}

variable "mcp_auth_required" {
  description = "Whether hosted MCP requests require authentication."
  type        = bool
  default     = true
}

variable "mcp_allowed_origins" {
  description = "Comma-separated list of allowed browser origins for /mcp."
  type        = string
  default     = ""
}

variable "mcp_allow_originless_clients" {
  description = "Whether non-browser clients may omit Origin."
  type        = bool
  default     = true
}

variable "session_backend" {
  description = "Shared session backend used by the hosted deployment."
  type        = string
  default     = "redis"

  validation {
    condition     = contains(["redis"], var.session_backend)
    error_message = "session_backend must be redis for hosted durability."
  }
}

variable "session_durability_required" {
  description = "Whether readiness should require a healthy shared session backend."
  type        = bool
  default     = true
}

variable "session_ttl_seconds" {
  description = "How long inactive sessions remain reusable."
  type        = number
  default     = 1800
}

variable "session_replay_ttl_seconds" {
  description = "How long replay events are retained for reconnect."
  type        = number
  default     = 300
}

variable "session_connectivity_model" {
  description = "Provider-specific connectivity model used by Cloud Run to reach the durable session backend."
  type        = string
  default     = "serverless_vpc_connector"
}

variable "managed_network_name" {
  description = "Optional override for the Terraform-managed VPC network name used by the hosted durable-session path."
  type        = string
  default     = ""
}

variable "secret_names" {
  description = "Secret names created as integration points for runtime deployment."
  type        = list(string)
  default     = ["YOUTUBE_API_KEY", "MCP_AUTH_TOKEN"]
}

variable "managed_subnet_name" {
  description = "Optional override for the Terraform-managed subnet name used by the hosted durable-session path."
  type        = string
  default     = ""
}

variable "managed_subnet_cidr" {
  description = "CIDR range reserved for the Terraform-managed durable-session subnet."
  type        = string
  default     = "10.8.0.0/28"
}

variable "managed_vpc_connector_name" {
  description = "Optional override for the Terraform-managed Serverless VPC Access connector name."
  type        = string
  default     = ""

  validation {
    condition     = var.managed_vpc_connector_name == "" || can(regex("^[a-z][-a-z0-9]{0,23}[a-z0-9]$", var.managed_vpc_connector_name))
    error_message = "managed_vpc_connector_name must match ^[a-z][-a-z0-9]{0,23}[a-z0-9]$ when set."
  }
}

variable "managed_vpc_connector_cidr" {
  description = "CIDR range reserved for the Terraform-managed Serverless VPC Access connector."
  type        = string
  default     = "10.8.1.0/28"
}

variable "managed_vpc_connector_min_throughput" {
  description = "Minimum throughput for the Terraform-managed Serverless VPC Access connector."
  type        = number
  default     = 200
}

variable "managed_vpc_connector_max_throughput" {
  description = "Maximum throughput for the Terraform-managed Serverless VPC Access connector."
  type        = number
  default     = 300
}

variable "redis_memory_size_gb" {
  description = "Redis instance size in GiB."
  type        = number
  default     = 1
}

variable "redis_tier" {
  description = "Redis service tier."
  type        = string
  default     = "BASIC"
}
