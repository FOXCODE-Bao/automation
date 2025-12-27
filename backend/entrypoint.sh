#!/bin/bash

set -e

echo "=========================================="
echo "Waiting for Database..."
echo "=========================================="

# Wait for PostgreSQL to be ready
# The DATABASE_URL should be in format: postgres://user:pass@host:port/dbname
if [ -n "$DATABASE_URL" ]; then
    # Extract host and port from DATABASE_URL if needed
    # For simplicity, we'll try to connect using Django's check
    python << END
import sys
import time
import psycopg2
import os
from urllib.parse import urlparse

database_url = os.environ.get('DATABASE_URL', '')
if database_url:
    result = urlparse(database_url)
    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname
    port = result.port

    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            conn = psycopg2.connect(
                dbname=database,
                user=username,
                password=password,
                host=hostname,
                port=port
            )
            conn.close()
            print("Database is ready!")
            break
        except psycopg2.OperationalError:
            retry_count += 1
            print(f"Database not ready yet. Attempt {retry_count}/{max_retries}...")
            time.sleep(2)
    else:
        print("Could not connect to database after maximum retries.")
        sys.exit(1)
END
fi

echo "=========================================="
echo "Running Database Migrations..."
echo "=========================================="
python manage.py migrate --noinput

echo "=========================================="
echo "Collecting Static Files..."
echo "=========================================="
python manage.py collectstatic --noinput

echo "=========================================="
echo "Starting Gunicorn Server..."
echo "=========================================="
exec gunicorn core.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
