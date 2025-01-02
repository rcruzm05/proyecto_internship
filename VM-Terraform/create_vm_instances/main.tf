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
}

  metadata = {
    startup-script = <<-EOT
      #!/bin/bash
      # Creacion de swap
      sudo dd if=/dev/zero of=/swapcito bs=1M count=512 
      sudo mkswap /swapcito
      sudo chmod 0600 /swapcito
      sudo swapon /swapcito
      sudo sh -c 'echo "/swapcito swap swap defaults 0 0" >> /etc/fstab' 
      # Instalar agentes de monitoreo
      curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
      sudo bash add-google-cloud-ops-agent-repo.sh --also-install
      sudo apt-get update
      sudo systemctl daemon-reload
      sudo apt update
      # Instalar herramienta para estresar la VM
      sudo apt install stress-ng -y
    EOT
  }

  tags = ["iap-access"]

  service_account {
    email  = "225988200293-compute@developer.gserviceaccount.com"
    scopes = [
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring.write",
      "https://www.googleapis.com/auth/devstorage.read_only"
    ]
  
  }
}
