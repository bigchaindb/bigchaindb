resource "azurerm_virtual_network" "bdb_node_VN_1" {
  name                = "bdb_node_VN_1"
  location            = "${var.location}"
  resource_group_name = "${azurerm_resource_group.bdb_node_RG.name}"
  address_space       = ["10.0.0.0/16"]
}
