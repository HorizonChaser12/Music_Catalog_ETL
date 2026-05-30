# Food Delivery ETL - Docker Example Setup

This repo is a shared data engineering project with my colleague Pranoti. It’s a playground for building multiple ETL pipelines using Airflow, Postgres, Spark, Redis, and a sample food delivery API.

## What this repo is for

This project is meant to capture a few different pipeline ideas in one place:

- orchestration using Airflow DAGs
- ingestion from a sample food delivery API
- transformation logic in Python and Spark
- analytics storage in PostgreSQL
- local development with Docker Compose

It’s a place to try new pipelines, compare them, and keep the structure reusable.

## Architecture

This project is built as a small, containerized data platform that is easy to extend as we add more ETL pipelines.
It’s designed around a few core ideas:

- keep services separate so each part can be updated independently
- orchestrate workflows in Airflow using DAGs
- keep ingestion and transformation logic modular
- use Docker Compose for a reproducible local development stack

### Key components

- `docker-compose.yml` defines the runtime stack for local development and testing.
- `airflow/dags/` contains DAG definitions and task orchestration logic.
- `ingestion/` contains the code for pulling data from the sample API.
- `transformations/` contains the cleaning, joining, and prep logic.
- `PostgreSQL` is the main analytics store for processed results.
- `Spark` is there to support future scalable processing, even if the current pipeline is small.

### Data flow diagram

```text
[Food Delivery API] ---> [Airflow DAG / scheduler]
         |                     |
         |                     v
         |             [Ingestion tasks]
         |                     |
         v                     v
   [Source data] -> [Transformations / Spark] -> [PostgreSQL]
                                             |
                                             v
                                     [Analytics / monitoring]
```

In short, Airflow triggers the pipeline, ingestion code pulls the data, transformation code cleans and enriches it, and PostgreSQL stores the final results.

### Why this architecture works

- Airflow gives us a clear place to manage dependencies, retries, and pipeline scheduling.
- Docker Compose keeps the local stack simple and reproducible.
- Splitting ingestion, transformation, and orchestration makes the repo easier to extend later.
- PostgreSQL gives a stable place to store results, so the output is easy to query and validate.

This setup is meant to showcase good data engineering habits: modular services, repeatable runs, and a clean separation between ingestion, transformation, orchestration, and storage.

## Pipelines

We are tracking multiple DAGs here. The idea is to keep a short summary for each pipeline and update it as we add more.

- **User Registration Analytics Pipeline**
  - tracks new users, locations, and country registration analytics
  - uses the sample food delivery API as source data
  - stores cleaned output in PostgreSQL
  - current status: example pipeline in `airflow/dags`

- **Future pipelines**
  - add new DAG name here
  - describe what it does, what data it uses, and where it writes results
  - include any special notes or dependencies

### How to add a pipeline

1. Add a new DAG file under `airflow/dags`
2. Add a short summary to this section
3. Keep the pipeline logic and dependencies as simple as possible at first

## Current pipeline flow

For the example DAG, the flow is roughly:

```bash
Start
  ↓
Fetch Countries API
  ↓
Fetch Locations API
  ↓
Fetch Users API
  ↓
Transform & clean data
  ↓
Join users with country/location
  ↓
Store into PostgreSQL
  ↓
Generate analytics table
  ↓
End
```

## Repo layout

- `airflow/dags/` — DAG definitions and Airflow workflows
- `ingestion/` — API fetch and data pull logic
- `transformations/` — cleaning and processing code
- `sql/` — SQL queries and table definitions
- `data/raw/` — sample raw data files
- `data/processed/` — sample processed output

## Included sample files

- `Dockerfile.example` — example Airflow container build file
- `docker-compose.example.yml` — sample Compose stack for Airflow, Postgres, Spark, Redis, pgAdmin, and the API
- `entrypoint.example.sh` — example startup script for Airflow that waits for Postgres and creates an admin user
- `.env.example` — example env file for local config

## Usage

1. Copy the example files if you want to customize the setup:

   ```bash
   cp Dockerfile.example Dockerfile
   cp docker-compose.example.yml docker-compose.yml
   cp entrypoint.example.sh entrypoint.sh
   cp .env.example .env
   chmod +x entrypoint.sh
   ```

2. Edit `.env` and `docker-compose.yml` as needed for your local settings.

3. Start the stack:

   ```bash
   docker compose up --build
   ```

4. Open the services:

   - Airflow webserver: `http://localhost:8082`
   - Spark master UI: `http://localhost:8080`
   - pgAdmin: `http://localhost:5050`
   - Food delivery API: `http://localhost:4000`

To stop the stack:

```bash
docker compose down
```

## Notes

- This repo is intended for local testing and learning, not production.
- Don’t commit passwords or real secrets into Git.
- Use `.env` or Docker secrets for configs you want to keep private.
