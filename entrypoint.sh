#!/bin/bash

# TODO: Validate RABBITMQ_URI is set

export RABBIT_HOST=$(echo ${RABBITMQ_URI} | cut -d'@' -f 2 | cut -d':' -f 1)
export RABBIT_PORT=$(echo ${RABBITMQ_URI} | cut -d':' -f 4 | cut -d'/' -f 1)

# Wait for RabbitMQ
while ! nc -z ${RABBIT_HOST} ${RABBIT_PORT}; do echo Waiting for RabbitMQ: ${RABBIT_HOST}:${RABBIT_PORT}; sleep 3; done;

# Then run the API server
# FIXME: replace with case statement (for default or override, e.g. bash)
if [[ "$1" == "server" ]];
then
  python ./server.py
else
  python ./agent.py
fi