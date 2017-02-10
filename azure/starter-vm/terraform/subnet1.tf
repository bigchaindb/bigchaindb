resource "azurerm_subnet" "bdb_node_subnet_1" {
  name                      = "bdb_node_subnet_1"
  resource_group_name       = "${azurerm_resource_group.bdb_node_RG.name}"
  virtual_network_name      = "${azurerm_virtual_network.bdb_node_VN_1.name}"
  address_prefix            = "10.0.2.0/24"
  network_security_group_id = "${azurerm_network_security_group.bdb_node_NSG_1.id}"
}
