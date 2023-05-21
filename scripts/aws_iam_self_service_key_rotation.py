#!/usr/bin/env python3
"""
Jenna Sprattler | SRE Kentik | 2023-04-13
Self service API access key rotation tool for IAM users
New users need to create initial keys via Web UI and run `aws configure` locally
Ref https://aws.amazon.com/blogs/security/how-to-rotate-access-keys-for-iam-users/
To rotate access keys, you should follow these steps:
1. Create a second access key in addition to the one in use.
2. Update all your applications to use the new access key and validate applications are working.
3. Change the state of the previous access key to inactive.
4. Validate that your applications are still working as expected.
5. Delete the inactive access key.
"""

import argparse
from pathlib import Path
import boto3

client = boto3.client('iam')
path = Path.home().joinpath(".aws/credentials")

def parse_args():
    """ Define cli args to be parsed into main()"""
    parser = argparse.ArgumentParser(description="create|update|delete|list API access keys")
    parser.add_argument('-c', '--create', action='store_true',
                        help="create access key")
    parser.add_argument('-u', '--update', type=str, nargs=2,
                        help="update access key; 2 expected inputs: <keyID> <active|inactive>")
    parser.add_argument('-d', '--delete', type=str, nargs=1,
                        help="delete access key; 1 expected input: <keyID>")
    parser.add_argument('-l', '--list', action='store_true',
                        help="list access key ID, status, creation date")
    args = parser.parse_args()
    return args

def main():
    """ API access key rotation """
    args = parse_args()
    if args.create:
        try:
            response = client.create_access_key()
            new_key = response['AccessKey']['AccessKeyId']
            new_secret = response['AccessKey']['SecretAccessKey']
            print(f"New Key:        %s" % new_key)
            print(f"Secret:         %s" % new_secret)
            print(f"\nMetadata response output:\n%s" % response, "\n")
            update_creds = input(
                f"Update {str(path)} file w/ new key (y/n)? "\
                "Warning: File contents will be overwritten! "
            )
            if update_creds.lower() == 'y':
                with open(path, "w", encoding="utf-8") as file:
                    lines = [
                        "[default]\n", "aws_access_key_id = " + new_key + "\n",
                        "aws_secret_access_key = " + new_secret + "\n"
                        ]
                    file.writelines(lines)
                    file.close()
                    with open(path, "r", encoding="utf-8") as file:
                        content = file.read()
                        print(f"\nUpdated {str(path)} file contents:\n%s" % content)
            else:
                print(f"\nYou answered 'n' or provided incorrect input, bye!")
        except client.exceptions.LimitExceededException as error:
            print(f"Access key limit exceeded, delete 1 of your keys: %s" % error)
    elif args.update:
        if args.update[1].lower() == 'active':
            response = client.update_access_key(
                AccessKeyId=args.update[0],
                Status='Active',
            )
            print(f"Metadata response output:\n%s" % response)
        elif args.update[1].lower() == 'inactive':
            response = client.update_access_key(
                AccessKeyId=args.update[0],
                Status='Inactive',
            )
            print(f"Metadata response output:\n%s" % response)
        else:
            print(f"Status: {args.update[1]} is not an option!")
    elif args.delete:
        response = client.delete_access_key(
            AccessKeyId=args.delete[0]
        )
        print(f"{args.delete[0]} has been deleted!\n")
        print(f"Metadata response output:\n%s" % response)
    elif args.list:
        for key in client.list_access_keys()['AccessKeyMetadata']:
            print(f"Key:        {(key['AccessKeyId'])}")
            print(f"Status:     {(key['Status'])}")
            print(f"Created:    {(key['CreateDate'])}\n")

if __name__ == "__main__":
    main()
