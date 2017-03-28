# Configure the Microsoft Azure Provider

# Why define these variables here? This is why:
# https://github.com/hashicorp/terraform/issues/7894#issuecomment-259758331
variable "subscription_id" {}
variable "client_id" {}
variable "client_secret" {}
variable "tenant_id" {}

provider "azurerm" {
  subscription_id = "${var.subscription_id}"
  client_id       = "${var.client_id}"
  client_secret   = "${var.client_secret}"
  tenant_id       = "${var.tenant_id}"
}
