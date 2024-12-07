import smtplib

port = 8025
smtp_server = "smtpd"
sender_email = "test@mail.com"
password = "toor"


def send(receiver_email, message):
    with smtplib.SMTP(smtp_server, port) as server:
        server.sendmail(sender_email, receiver_email, message)
