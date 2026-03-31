resource "google_compute_network" "hosted" {
  name                    = local.managed_network_name
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "hosted" {
  name          = local.managed_subnet_name
  ip_cidr_range = var.managed_subnet_cidr
  region        = var.region
  network       = google_compute_network.hosted.id
}

resource "google_vpc_access_connector" "cloud_run" {
  name          = local.managed_vpc_connector_name
  region        = var.region
  network       = google_compute_network.hosted.name
  ip_cidr_range = var.managed_vpc_connector_cidr
  min_throughput = var.managed_vpc_connector_min_throughput
  max_throughput = var.managed_vpc_connector_max_throughput
}
