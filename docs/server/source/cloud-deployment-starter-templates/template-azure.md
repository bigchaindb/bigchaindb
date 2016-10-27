# Template: Node Deployment on Azure

If you didn't read the introduction to the [cloud deployment starter templates](index.html), please do that now. The main point is that they're not for deploying a production node; they can be used as a starting point.

One can deploy a BigchainDB node on Azure using the template in [Microsoft's azure-quickstart-templates repository on GitHub](https://github.com/Azure/azure-quickstart-templates):

1. Go to [the /blockchain subdirectory in that repository](https://github.com/Azure/azure-quickstart-templates/tree/master/blockchain).

2. Click the button labelled **Deploy to Azure**.

3. If you're not already logged in to Microsoft Azure, then you'll be prompted to login. If you don't have an account, then you'll have to create one.

4. One you are logged in to the Microsoft Azure Portal, you should be taken to a form titled **Blockchain Template**. Below there are some notes to help with filling in that form.

5. Deployment takes a few minutes. You can follow the notifications by clicking the bell icon at the top of the screen. When done, you should see a notification saying "Deployment to resource group '[your resource group name]' was successful." The install script (`bigchaindb.sh`) installed RethinkDB, configured it using the default RethinkDB config file, and ran it. It also used pip to install [the latest `bigchaindb` from PyPI](https://pypi.python.org/pypi/BigchainDB).

6. Find out the public IP address of the virtual machine in the Azure Portal. Example: `40.69.87.250`

7. ssh in to the virtual machine at that IP address, e.g. `ssh adminusername@40.69.87.250` (where `adminusername` should be replaced by the Admin Username you entered into the form, and `40.69.87.250` should be replaced by the IP address you found in the last step).

8. You should be prompted for a password. Enter the Admin Password you entered into the form.

9. Configure BigchainDB using the default BigchainDB settings: `bigchaindb -y configure`

10. Run BigchainDB: `bigchaindb start`

BigchainDB should now be running on the Azure VM.

Remember to shut everything down when you're done (via the Azure Portal), because it generally costs money to run stuff on Azure.


## Notes on the Blockchain Template Form Fields

**Resource group** - You can use an existing resource group (if you have one) or create a new one named whatever you like, but avoid using fancy characters in the name because Azure might have problems if you do.

**Location** is the Microsoft Azure data center where you want the BigchainDB node to run. Pick one close to where you are located.

**Vm Dns Prefix** - Once your virtual machine (VM) is deployed, it will have a public IP address and a DNS name (hostname) something like `DNSprefix.northeurope.cloudapp.azure.com`. The `DNSprefix` will be whatever you enter into this field.

You can use whatever **Admin Username** and **Admin Password** you like (provided you don't get too fancy). It will complain if your password is too simple. You'll need these later to ssh into the VM.

**Blockchain Software** - Select `bigchaindb`.

For **Vm Size**, select `Standard_D1_v2` or better.

**\_artifacts Location** - Leave this alone.

**\_artifacts Location Sas Token** - Leave this alone (blank).

Don't forget to scroll down and check the box to agree to the terms and conditions.

Once you've finished the form, click the button labelled **Purchase**. (Generally speaking, it costs money to run stuff on Azure.)
