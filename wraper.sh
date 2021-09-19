#!/bin/bash

/usr/bin/redis-server /usr/local/battleships/redis.conf &
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start redis: $status"
  exit $status
fi

./backend/manage.py runserver 0.0.0.0:8000 &
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start django: $status"
  exit $status
fi

./backend/manage.py runworker message-delivery &
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start django-worker: $status"
  exit $status
fi

cd front && npm run dev
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start node: $status"
  exit $status
fi
