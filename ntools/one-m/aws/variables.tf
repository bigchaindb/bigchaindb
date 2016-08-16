variable "aws_region" {
  default = "eu-central-1"
}

variable "aws_instance_type" {
  default = "m4.xlarge"
}

variable "root_storage_in_GiB" {
  default = 10
}

variable "DB_storage_in_GiB" {
  default = 30
}
