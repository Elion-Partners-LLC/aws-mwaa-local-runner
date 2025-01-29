FROM python:3.9.17-bullseye

RUN apt-get update

WORKDIR /usr/src/

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ .
