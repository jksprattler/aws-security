#!/usr/bin/env python3
"""
Simple AWS IAM user account password reset script using boto3
Can output a list of existing IAM usernames to supply for reset
To be run by an AWS user w/ User Admin privileges
"""

import argparse
import secrets
import string
import boto3

resource = boto3.resource('iam')
client = boto3.client("iam")

def passwordgen():
    """
    Generate temporary strict password
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                                    description='List/Reset user accounts, output temp password')
    subparser = parser.add_subparsers(dest='command')
    list = subparser.add_parser('list')
    reset = subparser.add_parser('reset')

    list.add_argument('--list', help='List AWS IAM users')
    reset.add_argument('--reset', help='Reset password')
    reset.add_argument('-u', "--username", type=str,
                       required=True, help='AWS IAM Username')
    args = parser.parse_args()

    if args.command == 'list':
        for user in client.list_users()['Users']:
            print(f"User: {(user['UserName'])}")
    elif args.command == 'reset':
        PWD = passwordgen()
        client.update_login_profile(UserName=args.username,
                                    Password=PWD, PasswordResetRequired=True)
        print(args.username, 'Temp password:')
        print(PWD)
