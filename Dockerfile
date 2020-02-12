FROM python:3.7

WORKDIR /opt/app

RUN pip install requests lxml fastapi uvicorn jinja2

COPY . .

ENV PORT=8008

EXPOSE "${PORT}"

CMD uvicorn --host 0.0.0.0 --port "${PORT}" script_facade.main:app --reload
