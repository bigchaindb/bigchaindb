# You can get the value of "ip_address" after running terraform apply using:
# $ terraform output ip_address
# You could use that in a script, for example
output "ip_address" {
    value = "${aws_eip.ip.public_ip}"
}
