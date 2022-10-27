#!/bin/sh

set -e

if [ -z "$DATABASE_URI" ]
then
  echo "\$DATABASE_URI is empty!"
  exit 1
fi

echo "Waiting for DB $DATABASE_URI..."

while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
    echo "Not yet..."
    sleep 1
done

echo "DB is started!"

if [ "$DO_MIGRATE" = "True" ]
then
  python manage.py migrate
fi

exec "$@"