#!/bin/bash
set -e

host="$1"
shift

until nc -z -v -w30 $host 5672; do
  echo 'Waiting for RabbitMQ...'
  sleep 1
done

exec "$@"
