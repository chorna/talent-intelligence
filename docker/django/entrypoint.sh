#!/bin/sh

set -e

echo "Esperando PostgreSQL..."

until pg_isready \
    -h "$POSTGRES_HOST" \
    -p "$POSTGRES_PORT" \
    -U "$POSTGRES_USER"
do
    sleep 1
done

echo "PostgreSQL listo"

python manage.py migrate

exec python manage.py runserver 0.0.0.0:8000