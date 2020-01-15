FROM python:3.7

WORKDIR /opt/app

RUN pip install requests

COPY . .

CMD python3 script_facade/cli.py
