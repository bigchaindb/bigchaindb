# Use this file for Terraform variables that:
# 1) you don't mind sharing with the world on GitHub (if default provided) or
# 2) you want Terraform to ask the user for at runtime (if no default provided)

# Secret variables should be put in secret.tfvars with the following contents:
# subscription_id = "..."
# client_id = "..."
# client_secret = "..."
# tenant_id = "..."
# The secret.tfvars file will be read if you use:
# $ terraform <subcommand> -var-file="secret.tfvars"

variable "location" {
  default = "westeurope"
}
