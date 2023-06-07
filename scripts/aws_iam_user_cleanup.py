"""
Jenna Sprattler | SRE Kentik | 2023-06-07
Script to cleanup hardware/virtual MFA devices and login
profiles prior to deleting user programmatically from e.g.
Terraform where these settings are managed outside of the code.
"""

import sys
import boto3

client = boto3.client('iam')

def check_username():
    """ Check if username argument is provided and the user exists """
    if len(sys.argv) < 2 or sys.argv[1] == "--help":
        print("Usage: python aws_iam_user_cleanup.py <username>")
        return None

    user_name = sys.argv[1]
    existing_users = [user["UserName"] for user in client.list_users()["Users"]]

    if user_name not in existing_users:
        print(f"The user '{user_name}' does not exist.")
        return None

    return user_name

def delete_login_profile(user_name):
    """ Delete the login profile for the user """
    try:
        client.delete_login_profile(UserName=user_name)
        print(f"Deleting login profile for {user_name}")
    except client.exceptions.NoSuchEntityException:
        print(f"No login profile exists for {user_name}")

def delete_mfa_devices(user_name):
    """ Get the list of MFA devices for the user and delete each MFA device """
    response = client.list_mfa_devices(UserName=user_name)
    mfa_devices = response.get('MFADevices', [])

    if not mfa_devices:
        print(f"No MFA devices found for {user_name}")
        return

    for device in mfa_devices:
        device_name = device['SerialNumber']
        print(f"Deleting MFA device for {user_name}: {device_name}")
        client.deactivate_mfa_device(UserName=user_name, SerialNumber=device_name)

def main():
    """ Get the IAM username argument and proceed with cleanup only if username is valid """
    user_name = check_username()

    if user_name:
        delete_login_profile(user_name)
        delete_mfa_devices(user_name)

if __name__ == "__main__":
    main()
