FROM python:3.8.16-bullseye
MAINTAINER "Jesús Pérez <jesus_perez_ic@elionpartners.com>"

RUN apt-get update

WORKDIR /usr/src/

#install python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

RUN mkdir data
COPY src/ .
ENTRYPOINT ["python3", "logic.py"]
