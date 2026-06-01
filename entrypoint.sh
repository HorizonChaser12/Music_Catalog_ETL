#!/bin/bash
set -e

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z postgres 5432; do
  sleep 1
done
echo "Database is ready!"

# Initialize database
echo "Initializing Airflow database..."
airflow db migrate

# Create default admin user if it doesn't exist
echo "Creating default admin user..."
airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com \
  --password admin \
  2>/dev/null || echo "Admin user already exists"

echo "Airflow setup complete!"

# Execute the main airflow command
exec airflow "$@"
