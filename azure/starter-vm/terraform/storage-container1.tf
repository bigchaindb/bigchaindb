resource "azurerm_storage_container" "bdb_node_SC_1" {
  name                  = "bdbnodestoragecontainer1"
  resource_group_name   = "${azurerm_resource_group.bdb_node_RG.name}"
  storage_account_name  = "${azurerm_storage_account.bdb_node_SA.name}"
  container_access_type = "private"
}
