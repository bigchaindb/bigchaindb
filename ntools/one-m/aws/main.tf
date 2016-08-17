provider "aws" {
  # An AWS access_key and secret_key are needed; Terraform looks
  # for an AWS credentials file in the default location.
  # See https://tinyurl.com/pu8gd9h
  region = "${var.aws_region}"
}

# https://www.terraform.io/docs/providers/aws/r/instance.html
resource "aws_instance" "instance" {
  ami           = "${lookup(var.amis, var.aws_region)}"
  instance_type = "${var.aws_instance_type}"
  tags {
    Name        = "BigchainDB_node"
  }
  ebs_optimized = true
  key_name      = "${var.ssh_key_name}"
  vpc_security_group_ids = ["${aws_security_group.node_sg1.id}"]
  root_block_device = {
    volume_type = "gp2"
    volume_size = "${var.root_storage_in_GiB}"
    delete_on_termination = true
  }
  # Enable EC2 Instance Termination Protection
  disable_api_termination = true
}

# This EBS volume will be used for database storage (not for root).
# https://www.terraform.io/docs/providers/aws/r/ebs_volume.html
resource "aws_ebs_volume" "db_storage" {
  type = "gp2"
  availability_zone = "${aws_instance.instance.availability_zone}"
  # Size in GiB (not GB!)
  size = "${var.DB_storage_in_GiB}"
  tags {
    Name = "BigchainDB_db_storage"
  }
}

# This allocates a new elastic IP address, if necessary
# and then associates it with the above aws_instance
resource "aws_eip" "ip" {
  instance = "${aws_instance.instance.id}"
  vpc      = true
}

# https://www.terraform.io/docs/providers/aws/r/volume_attachment.html
resource "aws_volume_attachment" "ebs_att" {
  # Why /dev/sdp? See https://tinyurl.com/z2zqm6n
  device_name = "/dev/sdp"
  volume_id   = "${aws_ebs_volume.db_storage.id}"
  instance_id = "${aws_instance.instance.id}"
}

# You can get the value of "ip_address" after running terraform apply using:
# $ terraform output ip_address
# You could use that in a script, for example
output "ip_address" {
    value = "${aws_eip.ip.public_ip}"
}
