#!/usr/bin/env python3
"""
Simple AWS IAM user account password reset script using boto3
Options include: list all existing AWS IAM users, Reset a user's
password and create a login profile for Console UI access
To be run by an AWS user w/ User Admin privileges
"""

import argparse
import secrets
import string
import boto3

client = boto3.client('iam')

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

def parse_args():
    """ Define cli args to be parsed into main()"""
    parser = argparse.ArgumentParser(
                description="List/Reset/Create profiles for user accounts, output temp password")
    subparser = parser.add_subparsers(dest='command')
    subparser.add_parser('list-users', help="List AWS IAM users")
    reset = subparser.add_parser('reset', help="Reset a user password")
    reset.add_argument('-u', '--username', type=str,
                        required=True, help="AWS IAM Username")
    profile = subparser.add_parser('profile', help="Create user login profile")
    profile.add_argument('-u', '--username', type=str,
                        required=True, help="AWS IAM Username")
    args = parser.parse_args()
    return args

def main():
    """ List, reset or create login profiles for user accounts and output temp password """
    args = parse_args()
    pwd = passwordgen()
    if args.command == 'list-users':
        for user in client.list_users()['Users']:
            print(f"User: {(user['UserName'])}")
    elif args.command == 'reset':
        client.update_login_profile(UserName=args.username,
                                    Password=pwd, PasswordResetRequired=True)
        print('Password has been reset for:', args.username)
        print('Login with temp password:')
        print(pwd)
        print('Password reset will be enforced upon initial login')
    elif args.command == 'profile':
        client.create_login_profile(UserName=args.username,
                                    Password=pwd, PasswordResetRequired=True)
        print('New login profile has been created for:', args.username)
        print('Login with temp password:')
        print(pwd)
        print('Password reset will be enforced upon initial login')

if __name__ == "__main__":
    main()
