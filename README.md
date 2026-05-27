# Food Delivery ETL - Docker Example Setup

This repository includes example Docker files that can be used as a public reference without exposing private credentials.

## Included sample files

- `Dockerfile.example` - example Airflow container build file.
- `docker-compose.example.yml` - example Compose stack for Airflow, Postgres, Spark, and pgAdmin.
- `entrypoint.example.sh` - example startup script for Airflow that waits for Postgres and creates an admin user.
- `.env.example` - environment variable examples for sensitive values.

## Usage

1. Copy the example files for your own project:

   ```bash
   cp Dockerfile.example Dockerfile
   cp docker-compose.example.yml docker-compose.yml
   cp entrypoint.example.sh entrypoint.sh
   cp .env.example .env
   chmod +x entrypoint.sh
   ```

2. Edit `.env` and `docker-compose.yml` to set your own secure passwords and connection strings.

3. Start the stack with Docker Compose:

   ```bash
   docker compose up --build
   ```

4. Access services:

   - Airflow webserver: `http://localhost:8082`
   - Spark master UI: `http://localhost:8080`
   - pgAdmin: `http://localhost:5050`

## Security note

Do not commit any real passwords or private secrets into Git. Use `.env` and Docker secrets for your own deployments.
