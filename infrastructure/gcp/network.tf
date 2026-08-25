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

resource "google_compute_subnetwork" "direct_vpc_egress" {
  name          = local.managed_direct_vpc_subnet_name
  ip_cidr_range = var.managed_direct_vpc_subnet_cidr
  region        = var.region
  network       = google_compute_network.hosted.id
}
