FROM python:3.7

WORKDIR /opt/app

# cache hack; very fragile
COPY requirements.txt ./
RUN pip install --requirement requirements.txt

COPY . .


ENV FLASK_APP=script_facade/app:create_app() \
    FLASK_ENV=development \
    PORT=8008

EXPOSE "${PORT}"

CMD gunicorn --bind "0.0.0.0:${PORT:-8000}" ${FLASK_APP}
