"""
Jenna Sprattler | SRE Kentik | 2023-05-21
lambda function to send email notifications (SES) to users when passwords are expiring
based on a strict password policy w/ max password age of 90 days
"""
import time
from datetime import datetime
from dateutil import parser
import boto3

iam_client = boto3.client('iam')
ses_client = boto3.client('ses')

def lambda_handler(event, context):
    """ Get IAM creds report, check for expiring passwords & notify users """
    iam_client.generate_credential_report()

    while True:
        # Wait before checking the report status again
        time.sleep(5)

        # Get the credential report generation status
        response = iam_client.get_credential_report()
        if 'Content' in response:
            break

    credential_report = iam_client.get_credential_report()
    credential_report_csv = credential_report['Content'].decode('utf-8')

    # Process the credential report
    users_to_notify = []
    for line in credential_report_csv.split('\n')[1:]:
        fields = line.split(',')
        username = fields[0]
        password_last_changed = fields[5]

        if password_last_changed not in ('N/A', 'not_supported'):
            # Parse the date and time components from the timestamp
            password_last_changed_date = parser.parse(password_last_changed)
            days_since_password_change = (
                datetime.now() - password_last_changed_date.replace(tzinfo=None)).days

            if days_since_password_change > 78:
                # Retrieve user's email address from tags
                response = iam_client.list_user_tags(UserName=username)
                email = None
                for tag in response['Tags']:
                    if tag['Key'] == 'email':
                        email = tag['Value']
                        break
                if email:
                    users_to_notify.append({'username': username, 'email': email})

    # Send email notifications
    for user in users_to_notify:
        username = user['username']  # Get the username for the current user in the notify list
        message = f'''
            <html>
            <body>
                <p>Hello {username},</p>
                <p>Your password to access the <a href="https://signin.aws.amazon.com/console">AWS web console</a> has expired or will be expiring within the next 12 days.</p>
                <p>If your password is still valid, please log into the web console and follow the banner instructions to reset your password now.</p>
                <p>If you have API access keys configured, you can use the Password Reset Self Service <a href="https://github.com/jksprattler/aws-security/blob/main/scripts/aws_iam_self_service_password_reset.py">script</a>.</p>
                <p>If you don't use API keys, and your password has passed the expiration date then reply to this email and we'll assist with your password reset.</p>
                <p>If you don't use your AWS account, reply to this email and we'll remove your account.</p>
                <br>
                <p>Thank you,</p>
                <p>Cloud Admins</p>
            </body>
            </html>
            '''
        ses_client.send_email(
            Source='cloud-admins@jennasrunbooks.com',
            Destination={'ToAddresses': [user['email']]},
            Message={
                'Subject': {'Data': 'AWS Password Expiry Notification'},
                'Body': {'Html': {'Data': message}}
            }
        )

    return 'Password expiry notifications sent.'
