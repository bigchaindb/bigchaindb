variable "aws_region" {
  default = "eu-central-1"
}

variable "aws_instance_type" {
  default = "m4.large"
}

variable "root_storage_in_GiB" {
  default = 10
}

variable "DB_storage_in_GiB" {
  default = 30
}

variable "ssh_key_name" {
  # No default. Ask as needed.
}
