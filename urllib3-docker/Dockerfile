# https://docs.docker.com/language/python/build-images/
FROM python:alpine3.16

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

