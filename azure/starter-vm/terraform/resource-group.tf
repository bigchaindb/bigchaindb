resource "azurerm_resource_group" "bdb_node_RG" {
  name     = "bdb_node_RG"
  location = "${var.location}"
}
