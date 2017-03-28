resource "azurerm_public_ip" "bdb_node_IP_1" {
  name                         = "bdb_node_IP_1"
  location                     = "${var.location}"
  resource_group_name          = "${azurerm_resource_group.bdb_node_RG.name}"
  public_ip_address_allocation = "static"
}

output "bdb_node_IP_1" {
  value = "${azurerm_public_ip.bdb_node_IP_1.ip_address}"
}
