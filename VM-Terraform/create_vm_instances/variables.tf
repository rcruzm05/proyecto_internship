variable "project_id" {
  default = "sit-devops-training"
  type    = string
}

variable "region" {
  default = "us-central1"
  type    = string
}

variable "zone" {
  type    = string
  default = "us-central1-c"
}

variable "instance_count" {
  type    = number
  #default = 3
}

variable "instance_name_prefix" {
  type    = string
  default = "tf-instance"
}

variable "machine_type" {
  default = "e2-micro"
  type    = string
}

variable "boot_disk_image" {
  default     = "debian-cloud/debian-12"
  type        = string
}

variable "network" {
  default = "vpc-liverpool"
  type    = string
}

variable "subnetwork" {
  default = "subnet-liverpool"
  type    = string
}

variable "service_account_email" {
  type    = string
}

variable "tags" {
  default = ["iap-access"]
  type    = list(string)
}
