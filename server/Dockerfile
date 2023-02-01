FROM python:3.8-slim-buster

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN apt-get update && apt-get dist-upgrade
RUN apt-get install mysql-server
RUN apt-get install libmysqlclient-dev
RUN pip3 install flask-mysqldb
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
