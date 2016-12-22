# Azure Quickstart Template

If you didn't read the introduction to the [cloud deployment starter templates](index.html), please do that now. The main point is that they're not for deploying a production node; they can be used as a starting point.

Note: There was an Azure quickstart template in the `blockchain` directory of Microsoft's `Azure/azure-quickstart-templates` repository on GitHub. It's gone now; it was replaced by the one described here.

One can deploy a BigchainDB node on Azure using the template in the `bigchaindb-on-ubuntu` directory of Microsoft's `Azure/azure-quickstart-templates` repository on GitHub. Here's how:

1. Go to [that directory on GitHub](https://github.com/Azure/azure-quickstart-templates/tree/master/bigchaindb-on-ubuntu).

1. Click the button labelled **Deploy to Azure**.

1. If you're not already logged in to Microsoft Azure, then you'll be prompted to login. If you don't have an account, then you'll have to create one.

1. Once you are logged in to the Microsoft Azure Portal, you should be taken to a form titled **BigchainDB**. Some notes to help with filling in that form are available [below](azure-quickstart-template.html#notes-on-the-blockchain-template-form-fields).

1. Deployment takes a few minutes. You can follow the notifications by clicking the bell icon at the top of the screen. At the time of writing, the final deployment operation (running the `init.sh` script) was failing, but a pull request ([#2884](https://github.com/Azure/azure-quickstart-templates/pull/2884)) has been made to fix that and these instructions say what you can do before that pull request gets merged...

1. Find out the public IP address of the virtual machine in the Azure Portal. Example: `40.69.87.250`

1. ssh in to the virtual machine at that IP address, i.e. do `ssh <Admin_username>@<machine-ip>` where `<Admin_username>` is the admin username you entered into the form and `<machine-ip>` is the virtual machine IP address determined in the last step. Example: `ssh bcdbadmin@40.69.87.250`

1. You should be prompted for a password. Give the `<Admin_password>` you entered into the form.

1. Configure BigchainDB Server by doing:
```text
bigchaindb configure
```
It will ask you several questions. You can press `Enter` (or `Return`) to accept the default for all of them *except for one*. When it asks **API Server bind? (default \`localhost:9984\`):**, you should answer:
```text
API Server bind? (default `localhost:9984`): 0.0.0.0:9984
```

Finally, run BigchainDB Server by doing:
```text
bigchaindb start
```

BigchainDB Server should now be running on the Azure virtual machine.

Remember to shut everything down when you're done (via the Azure Portal), because it generally costs money to run stuff on Azure.


## Notes on the Blockchain Template Form Fields

### BASICS

**Resource group** - You can use an existing resource group (if you have one) or create a new one named whatever you like, but avoid using fancy characters in the name because Azure might have problems if you do.

**Location** is the Microsoft Azure data center where you want the BigchainDB node to run. Pick one close to where you are located.

### SETTINGS

You can use whatever **Admin\_username** and **Admin\_password** you like (provided you don't get too fancy). It will complain if your password is too simple. You'll need these later to `ssh` into the virtual machine.

**Dns\_label\_prefix** - Once your virtual machine is deployed, it will have a public IP address and a DNS name (hostname) something like `<DNSprefix>.northeurope.cloudapp.azure.com`. The `<DNSprefix>` will be whatever you enter into this field.

**Virtual\_machine\_size** - This should be one of Azure's standard virtual machine sizes, such as `Standard_D1_v2`. There's a [list of virtual machine sizes in the Azure docs](https://docs.microsoft.com/en-us/azure/virtual-machines/virtual-machines-windows-sizes?toc=%2fazure%2fvirtual-machines%2fwindows%2ftoc.json).

**\_artifacts Location** - Leave this alone.

**\_artifacts Location Sas Token** - Leave this alone (blank).

### TERMS AND CONDITIONS

Read the terms and conditions. If you agree to them, then check the checkbox.

Finally, click the button labelled **Purchase**. (Generally speaking, it costs money to run stuff on Azure.)
