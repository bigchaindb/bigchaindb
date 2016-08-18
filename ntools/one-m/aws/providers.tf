provider "aws" {
  # An AWS access_key and secret_key are needed; Terraform looks
  # for an AWS credentials file in the default location.
  # See https://tinyurl.com/pu8gd9h
  region = "${var.aws_region}"
}
