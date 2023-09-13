variable "user_info" {
  description = "Map of AWS IAM usernames, email address tags and custom user tags"
  type = map(object({
    email     = string
    user_tags = optional(map(string))
  }))
  default = {
    "userA" = {
      email = "userA@jennasrunbooks.com"
    }
    "userB" = {
      email = "userB@jennasrunbooks.com"
      user_tags = {
        "AKIASRJ6UGTMV3JU6CU2" = "testkey1"
      }
    }
  }
}


resource "aws_iam_user" "this" {
  for_each = var.user_info
  name     = each.key
  path     = "/"
  tags = merge(
    var.common_tags,
    {
      email = each.value.email
    },
    each.value.user_tags
  )
  # Provisions the login profile for each new user and outputs their temp login password
  provisioner "local-exec" {
    when    = create
    command = "python ../../scripts/aws_iam_user_password_reset.py profile -u ${each.key}"
  }
  # Destroys the login profile, MFA devices and access keys for each removed user
  provisioner "local-exec" {
    when    = destroy
    command = "python ../../scripts/aws_iam_user_cleanup.py ${each.key}"
  }
}
