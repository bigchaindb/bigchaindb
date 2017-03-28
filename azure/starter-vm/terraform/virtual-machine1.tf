variable "vm1_admin_password" {}

resource "azurerm_virtual_machine" "bdb_node_VM_1" {
  name                  = "bdb_node_VM_1"
  location              = "${var.location}"
  resource_group_name   = "${azurerm_resource_group.bdb_node_RG.name}"
  network_interface_ids = ["${azurerm_network_interface.bdb_node_NIC_1.id}"]
  vm_size               = "Standard_A2_v2"

  storage_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "16.04-LTS"
    version   = "latest"
  }

  storage_os_disk {
    name          = "vm1osdisk1"
    vhd_uri       = "${azurerm_storage_account.bdb_node_SA.primary_blob_endpoint}${azurerm_storage_container.bdb_node_SC_1.name}/vm1osdisk1.vhd"
    caching       = "ReadWrite"
    create_option = "FromImage"
  }

  storage_data_disk {
    name          = "vm1datadisk1"
    vhd_uri       = "${azurerm_storage_account.bdb_node_SA.primary_blob_endpoint}${azurerm_storage_container.bdb_node_SC_1.name}/vm1datadisk1.vhd"
    disk_size_gb  = "30"
    create_option = "empty"
    lun           = 0
  }

  os_profile {
    computer_name  = "vm1"
    admin_username = "vm1admin"
    admin_password = "${var.vm1_admin_password}"
  }

  os_profile_linux_config {
    disable_password_authentication = false
  }
}
