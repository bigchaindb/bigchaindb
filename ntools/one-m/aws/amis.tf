# Each AWS region has a different AMI name
# even though the contents are the same.
# This file has the mapping from region --> AMI name.
#
# These are all Ubuntu 16.04 LTS AMIs
# with Arch = amd64, Instance Type = hvm:ebs-ssd
# from https://cloud-images.ubuntu.com/locator/ec2/
# as of Jan. 31, 2017
variable "amis" {
  type = "map"
  default = {
    eu-west-1      = "ami-d8f4deab"
    eu-central-1   = "ami-5aee2235"
    us-east-1      = "ami-6edd3078"
    us-west-2      = "ami-7c803d1c"
    ap-northeast-1 = "ami-eb49358c"
    ap-southeast-1 = "ami-b1943fd2"
    ap-southeast-2 = "ami-fe71759d"
    sa-east-1      = "ami-7379e31f"
  }
}
