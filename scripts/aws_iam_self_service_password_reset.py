#!/usr/bin/env python3
"""
Jenna Sprattler | SRE Kentik | 2023-04-13
Simple self service password reset tool for clients
To be run by any AWS IAM user to reset their own password
"""

import secrets
import string
import botocore
import boto3

client = boto3.client('iam')

def passwordgen():
    """
    Generate new strict password
    """
    # define the alphabet
    letters = string.ascii_letters
    digits = string.digits
    special_chars = string.punctuation
    alphabet = letters + digits + special_chars
    # fix password length
    pwd_length = 20

    # generate a password string
    pwd = ''
    for _i in range(pwd_length):
        pwd += ''.join(secrets.choice(alphabet))
    return pwd

def main():
    """ Reset your IAM user password """
    pwd = passwordgen()
    try:
        old_password = input("Current password:\n")
        response = client.change_password(
            OldPassword=old_password,
            NewPassword=pwd
            )
        print(f"\nNew password:")
        print(pwd)
        print(f"\nMetadata response output:\n", response)
    except botocore.exceptions.ClientError as error:
        print(f"Unexpected error: %s" % error)
    except client.exceptions.PasswordPolicyViolationException as error:
        print(f"Password policy violation: %s" % error)
    except client.exceptions.EntityTemporarilyUnmodifiableException as error:
        print(f"Entity temporarily unmodifiable: %s" % error)

if __name__ == "__main__":
    main()
