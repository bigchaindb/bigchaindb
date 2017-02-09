# Create a resource group
resource "azurerm_resource_group" "bdbNodeRG" {
  name     = "bdbNodeRG"
  location = "${var.location}"
}