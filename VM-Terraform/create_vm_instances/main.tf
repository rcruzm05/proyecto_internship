provider "google" {
  project = "sit-devops-training"
  region  = "us-central1"
}

resource "google_compute_instance" "example" {
  count        = 1 # Cambia el número de instancias que deseas crear
  name         = "terraform-test-${count.index}"
  machine_type = "e2-micro"
  zone         = "us-central1-c"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12"
    }
  }

  network_interface {
    network = "vpc-liverpool"
    subnetwork = "subnet-liverpool"

    #access_config = null
}

  metadata = {
    startup-script = <<-EOT
      #!/bin/bash
      curl -sSO https://dl.google.com/cloudagents/add-monitoring-agent-repo.sh
      #sudo bash add-monitoring-agent-repo.sh
      sudo bash add-google-cloud-ops-agent-repo.sh --also-install
      sudo apt-get update
      sudo apt-get install -y stackdriver-agent
      sudo service stackdriver-agent start
    EOT
  }

  #tags = ["web", "cloud-monitoring"]
  tags = ["iap-access"]

  #service_account {
  #  email  = "default"
  #  scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  #}
}
