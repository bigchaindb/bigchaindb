# Install Terraform

The [Terraform documentation has installation instructions](https://www.terraform.io/intro/getting-started/install.html) for all common operating systems.

Note: Hashicorp (the company behind Terraform) will try to convince you that running Terraform on their servers (inside Atlas) would be great. **While that might be true for many, it is not true for BigchainDB.** BigchainDB federations are supposed to be decentralized, and if everyone used Atlas, that would be a point of centralization. If you don't want to run Terraform on your local machine, you could install it on a cloud machine under your control (e.g. on AWS).

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
