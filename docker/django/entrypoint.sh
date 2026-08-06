#!/bin/sh

set -e

echo "⏳ Waiting for PostgreSQL..."

until pg_isready -h db -p 5432 -U talent
do
    sleep 1
done

echo "✅ PostgreSQL is ready"

python manage.py migrate

if [ "$#" -gt 0 ]; then
    exec "$@"
fi

exec python manage.py runserver 0.0.0.0:8000