project_id                = "project-78870e9f-2b9f-4053-907"
region                    = "us-central1"
environment               = "staging"
service_name              = "youtube-mcp-server"
service_account_name      = "youtube-mcp-server"
public_invocation_intent  = "public_remote_mcp"
bootstrap_image_reference = "us-docker.pkg.dev/cloudrun/container/hello"
secret_access_mode        = "secret_manager_env"

min_instances   = 0
max_instances   = 2
concurrency     = 20
timeout_seconds = 180

mcp_auth_required            = true
mcp_allowed_origins          = "https://chat.openai.com"
mcp_allow_originless_clients = true

session_backend                = "redis"
session_connectivity_model     = "direct_vpc_egress"
managed_network_name           = "youtube-mcp-server-staging-network"
managed_subnet_name            = "youtube-mcp-server-staging-subnet"
managed_subnet_cidr            = "10.8.0.0/28"
managed_direct_vpc_subnet_name = "youtube-mcp-server-staging-direct-egress"
managed_direct_vpc_subnet_cidr = "10.8.2.0/26"
session_durability_required    = true
session_ttl_seconds            = 1800
session_replay_ttl_seconds     = 300

secret_names = [
  "YOUTUBE_API_KEY",
  "MCP_AUTH_TOKEN",
]
