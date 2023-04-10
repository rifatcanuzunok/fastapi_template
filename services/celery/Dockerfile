FROM python:3.10.8-slim-buster

WORKDIR /code

ENV DOCKER="TRUE"

COPY requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code

CMD celery -A services.celery.email.service worker --concurrency=4 -l info -Q email