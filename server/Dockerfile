# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /python-docker


COPY requirements.txt requirements.txt
RUN apt-get update -y && apt-get dist-upgrade -y
RUN apt-get update && apt-get install -y default-mysql-client
RUN apt-get install -y python-pip python-dev build-essential default-libmysqlclient-dev
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT [ "flask"]
CMD [ "run", "--host", "0.0.0.0","--port","8001"]