# Install Terraform

The [Terraform documentation has installation instructions](https://www.terraform.io/intro/getting-started/install.html) for all common operating systems.

If you don't want to run Terraform on your local machine, you can install it on a cloud machine under your control (e.g. on AWS).

Note: Hashicorp has an enterprise version of Terraform called "Terraform Enterprise." You can license it by itself or get it as part of Atlas. If you decide to license Terraform Enterprise or Atlas, be sure to install it on your own hosting (i.e. "on premise"), not on the hosting provided by Hashicorp. The reason is that BigchainDB clusters are supposed to be decentralized. If everyone used Hashicorp's hosted Atlas, then that would be a point of centralization.


## Ubuntu Installation Tips

If you want to install Terraform on Ubuntu, first [download the .zip file](https://www.terraform.io/downloads.html). Then install it in `/opt`:
```text
sudo mkdir -p /opt/terraform
sudo unzip path/to/zip-file.zip -d /opt/terraform
```

Why install it in `/opt`? See [the answers at Ask Ubuntu](https://askubuntu.com/questions/1148/what-is-the-best-place-to-install-user-apps).

Next, add `/opt/terraform` to your path. If you use bash for your shell, then you could add this line to `~/.bashrc`:
```text
export PATH="/opt/terraform:$PATH"
```

After doing that, relaunch your shell or force it to read `~/.bashrc` again, e.g. by doing `source ~/.bashrc`. You can verify that terraform is installed and in your path by doing:
```text
terraform --version
```

It should say the current version of Terraform.
