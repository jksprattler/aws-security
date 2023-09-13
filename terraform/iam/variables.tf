variable "common_tags" {
  type = map(any)
  default = {
    resource-owner   = "aws-landing-zone@jennasrunbooks.com"
    environment-type = "lab"
    provisioner      = "terraform"
    repo             = "aws-security"
  }
}
