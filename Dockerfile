# syntax=docker/dockerfile:1
FROM python:3.9-bullseye
ENV PYTHONUNBUFFERED=1
WORKDIR /usr/local/battleships/
COPY requirements.txt /usr/local/battleships/backend/
COPY wraper.sh /usr/local/battleships
COPY redis.conf /usr/local/battleships
RUN chmod +x wraper.sh
RUN pip install -r backend/requirements.txt
COPY backend/battleships /usr/local/battleships/backend/
RUN apt-get update && apt-get install --yes redis redis-server npm
#RUN apt-get update && apt-get install --yes apt-utils && apt-get install --yes npm redis
COPY front/ /usr/local/battleships/front/
WORKDIR /usr/local/battleships/front/
RUN npm install
WORKDIR /usr/local/battleships
CMD ./wraper.sh
