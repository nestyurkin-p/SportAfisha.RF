FROM python:3.12-bookworm

RUN python -m pip install aiosmtpd

CMD python -m aiosmtpd --debug --debug --listen 0.0.0.0:8025
