FROM python:3.9

RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install postgresql-client -y

COPY . /code
RUN chmod +x /code/wait-for-it.sh
WORKDIR /code

RUN pip install -r requirements.txt