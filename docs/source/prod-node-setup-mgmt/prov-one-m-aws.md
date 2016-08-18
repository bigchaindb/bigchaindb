# Provision a One-Machine Node on AWS

This page describes how to provision the resources needed for a one-machine BigchainDB node on AWS using Terraform.

## Get Set

First, do the [basic AWS setup steps outlined in the Appendices](../appendices/aws-setup.html).

Then go to the `.../bigchaindb/ntools/one-m/aws/` directory and open the file `variables.tf`. Most of the variables have sensible default values, but you can change them if you like. In particular, you may want to change `aws_region`. (Terraform looks in `~/.aws/credentials` to get your AWS credentials, so you don't have to enter those anywhere.)

The `ssh_key_name` has no default value, so Terraform will prompt you every time it needs it.

To see what Terraform will do, run:
```text
terraform plan
```

It should ask you the value of `ssh_key_name`. 

It figured out the plan by reading all the `.tf` Terraform files in the directory.

If you don't want to be asked for the `ssh_key_name`, you can change the default value of `ssh_key_name` or [you can set an environmen variable](https://www.terraform.io/docs/configuration/variables.html) named `TF_VAR_ssh_key_name`.


## Provision

To provision all the resources specified in the plan, do the following. **Note: This will provision actual resources on AWS, and those cost money. Be sure to shut down the resources you don't want to keep running later, otherwise the cost will keep growing.**
```text
terraform apply
```

Terraform will report its progress as it provisions all the resources. Once it's done, you can go to the Amazon EC2 web console and see the instance, its security group, its elastic IP, and its attached storage volumes (one for the root directory and one for RethinkDB storage).

At this point, there is no software installed on the instance except for Ubuntu 14.04 and whatever else came with the Amazon Machine Image (AMI) specified in the configuration. The next step is to use Ansible to install and configure all the necessary software.


## (Optional) "Destroy"

If you want to shut down all the resources just provisioned, you must first disable termination protection on the instance:

1. Go to the EC2 console and select the instance you just launched. It should be named `BigchainDB_node`.
2. Click **Actions** > **Instance Settings** > **Change Termination Protection** > **Yes, Disable**
3. Back in your terminal, do `terraform destroy`

Terraform should "destroy" (i.e. terminate or delete) all the AWS resources you provisioned above.

## See Also

* The [Terraform Documentation](https://www.terraform.io/docs/)
* The [Terraform Documentation for the AWS "Provider"](https://www.terraform.io/docs/providers/aws/index.html)
