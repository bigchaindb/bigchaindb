resource "azurerm_storage_account" "bdb_node_SA" {
  name                = "bdbnodestorageaccount"
  location            = "${var.location}"
  resource_group_name = "${azurerm_resource_group.bdb_node_RG.name}"
  account_type        = "Standard_LRS"
}
