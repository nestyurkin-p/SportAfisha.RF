import os
import boto3

from botocore.exceptions import ClientError

client = boto3.client(
    service_name="sesv2",
    endpoint_url="https://postbox.cloud.yandex.net",
    region_name="ru-central1",
)


def postbox_send(target_email, subject, message):
    charset = "UTF-8"
    sender = os.getenv("SENDER")
    try:
        print("Sending response")
        response = client.send_email(
            FromEmailAddress=sender,
            Destination={
                "ToAddresses": [
                    target_email,
                ],
            },
            Content={
                "Simple": {
                    "Subject": {"Data": subject, "Charset": charset},
                    "Body": {
                        "Text": {"Data": message, "Charset": charset},
                    },
                }
            },
        )
        print(response)
    except ClientError as e:
        print(e.response["Error"]["Message"])
    else:
        print("Email sent! Message ID: " + response["MessageId"])
