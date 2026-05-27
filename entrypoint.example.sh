#!/bin/bash
set -e

# Wait for Postgres database to be ready
until nc -z postgres 5432; do
  echo "Waiting for Postgres..."
  sleep 1
done

# Initialize Airflow DB and create admin user
airflow db upgrade

AIRFLOW_ADMIN_PASSWORD=${AIRFLOW_ADMIN_PASSWORD:-changeme}

airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com \
  --password "$AIRFLOW_ADMIN_PASSWORD" \
  2>/dev/null || true

exec airflow "$@"
