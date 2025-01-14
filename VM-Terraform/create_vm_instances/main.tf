resource "google_compute_instance" "example" {
  count        = var.instance_count
  name         = "${var.instance_name_prefix}-${count.index}"
  machine_type = var.machine_type
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = var.boot_disk_image
    }
  }

  network_interface {
    network    = var.network
    subnetwork = var.subnetwork
  }

  metadata = {
    startup-script = <<-EOT
      #!/bin/bash
      # Creación de swap
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

  tags = var.tags

  service_account {
    email  = var.service_account_email
    scopes = [
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring.write",
      "https://www.googleapis.com/auth/devstorage.read_only"
    ]
  }
}
