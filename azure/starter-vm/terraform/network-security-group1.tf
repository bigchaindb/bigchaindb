# Azure Network Security Group docs:
# https://www.terraform.io/docs/providers/azurerm/r/network_security_group.html
# https://docs.microsoft.com/en-us/azure/virtual-network/virtual-networks-nsg
resource "azurerm_network_security_group" "bdb_node_NSG_1" {
  name                = "bdb_node_NSG_1"
  location            = "${var.location}"
  resource_group_name = "${azurerm_resource_group.bdb_node_RG.name}"

  security_rule {
    name                       = "ssh"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"     # Tcp, Udp, or * for both
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}
