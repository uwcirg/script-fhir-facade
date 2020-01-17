FROM python:3.7

WORKDIR /opt/app

RUN pip install requests lxml fastapi uvicorn jinja2

COPY . .

EXPOSE 8000

CMD uvicorn --host 0.0.0.0 script_facade.main:app --reload
