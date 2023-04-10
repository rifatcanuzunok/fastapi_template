FROM python:3.10.8-slim-buster

WORKDIR /app

ENV DOCKER="TRUE"

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /app

CMD uvicorn main:app --host 0.0.0.0 --port 3654 --workers 4
