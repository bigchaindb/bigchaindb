# Each AWS region has a different AMI name
# even though the contents are the same.
# This file has the mapping from region --> AMI name.
#
# These are all Ubuntu 14.04 LTS AMIs
# with Arch = amd64, Instance Type = hvm:ebs-ssd
# from https://cloud-images.ubuntu.com/locator/ec2/
variable "amis" {
  type = "map"
  default = {
    eu-west-1      = "ami-55452e26"
    eu-central-1   = "ami-b1cf39de"
    us-east-1      = "ami-8e0b9499"
    us-west-2      = "ami-547b3834"
    ap-northeast-1 = "ami-49d31328"
    ap-southeast-1 = "ami-5e429c3d"
    ap-southeast-2 = "ami-25f3c746"
    sa-east-1      = "ami-97980efb"
  }
}
