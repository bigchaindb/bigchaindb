resource "azurerm_network_interface" "bdb_node_NIC_1" {
  name                = "bdb_node_NIC_1"
  location            = "${var.location}"
  resource_group_name = "${azurerm_resource_group.bdb_node_RG.name}"

  ip_configuration {
    name                          = "bdb_node_IP_config_1"
    subnet_id                     = "${azurerm_subnet.bdb_node_subnet_1.id}"
    private_ip_address_allocation = "dynamic"
    public_ip_address_id          = "${azurerm_public_ip.bdb_node_IP_1.id}"
  }
}
