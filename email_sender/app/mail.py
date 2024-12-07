import os
import boto3

from email.mime.text import MIMEText
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart


client = boto3.client(
    service_name="sesv2",
    endpoint_url="https://postbox.cloud.yandex.net",
    region_name="ru-central1",
)


def postbox_send(target_email, subject, message):
    SENDER = os.getenv("SENDER")
    CHARSET = "utf-8"

    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg_body = MIMEMultipart("alternative")
    textpart = MIMEText(message.encode(CHARSET), "plain", CHARSET)
    msg_body.attach(textpart)
    msg.attach(msg_body)

    try:
        print("Sending response")
        response = client.send_email(
            FromEmailAddress=SENDER,
            Destination={"ToAddresses": [target_email]},
            Content={
                "Raw": {
                    "Data": msg.as_string(),
                },
            },
        )
        print(response)
    except ClientError as e:
        print(e.response["Error"]["Message"])
    else:
        print("Email sent! Message ID: " + response["MessageId"]),
