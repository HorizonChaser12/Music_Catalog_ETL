# Music Catalog ETL

A shared data engineering project built to learn what it takes to turn a real external API into a reliable, reusable data pipeline with my project partner [Pranoti](https://github.com/Pranoti-2002).

We started with a simple idea: pull music metadata from the MusicBrainz API, clean it, store it in PostgreSQL, and make it available for analysis. As the project grew, the interesting part stopped being the music data itself and became the engineering around it — how to structure a pipeline, keep source data intact, track a run across multiple stages, validate that data actually moved correctly, and avoid rewriting the same operational logic for every new pipeline.

That is the direction of this repository.

## Why we built this

This is primarily a hands-on data engineering project.

The goal was not just to make an API-to-database script work once. We wanted to explore the pieces that start becoming important when an ETL pipeline needs to be repeatable and maintainable:

- How should raw source data be preserved?
- Where should cleansing and business transformations happen?
- How do we know which records belong to which pipeline run?
- How do we detect that data was lost between two stages?
- Which parts of an ETL pipeline should be specific to a dataset, and which should be reusable?
- How can multiple pipelines share the same operational framework?
- How do Airflow, Spark, Python and PostgreSQL fit together without making one component responsible for everything?

MusicBrainz gives us a useful real-world source for exploring these questions because its API responses are nested, relationship-heavy, and not naturally shaped like the tables we eventually want to query.

## What we built

The project has evolved into a small batch-oriented data platform:

```text
                  MusicBrainz API
                        |
                        v
                  Raw JSON data
                        |
                        v
                 +--------------+
                 |   Landing    |
                 |  PostgreSQL  |
                 +--------------+
                        |
                        v
                  Spark / PySpark
                        |
                        v
                 +--------------+
                 |  Sanitized   |
                 |  PostgreSQL  |
                 +--------------+
                        |
                        v
                 +--------------+
                 |   Curated    |
                 |  PostgreSQL  |
                 +--------------+

       Batch ID + Audit + Reconciliation
              run across the stages
```

The important part is the separation of responsibilities.

**Ingestion** is concerned with getting source data.

**Landing** is concerned with preserving that source data.

**Spark** is used when the nested source payload needs to be parsed and transformed into a structured model.

**Sanitized** data is the cleaner relational representation.

**Curated** data is shaped for a particular analytical purpose.

**Audit and reconciliation** sit across these stages to answer a different question: *did the pipeline actually process what it was supposed to process?*

Airflow provides the orchestration around these pieces rather than becoming the place where all the data transformation logic lives.

## The design that emerged

One of the biggest things we learned was that an ETL pipeline is not just:

```text
Extract -> Transform -> Load
```

There is operational state around that process.

A pipeline run needs an identity. Stages need to know which run they belong to. And simply having a successful Airflow task does not necessarily mean the expected number of records reached the next layer.

That led us to introduce a common batch and reconciliation model.

### Batch IDs

Each run gets an `etl_batch_id`.

The batch is recorded in:

```text
audit.batch_log
```

The same batch identity can then be carried through the different stages of the pipeline.

This gives us a common reference for questions such as:

```text
Which run produced these records?
Which phase is still incomplete?
How many records were processed?
Did this phase complete successfully?
What went wrong?
```

The current implementation generates IDs using the source system and execution timestamp, for example:

```text
20260730173828_cv1
```

The important idea is not the exact format. It is that the batch ID is treated as a pipeline-level identifier rather than something owned by one individual table.

### Reconciliation

We also learned that a pipeline can be technically "successful" while still producing incomplete data.

For example:

```text
Raw source records     = 1000
Landing records        = 1000
Sanitized records      = 997
```

Every task could finish without throwing an exception, but three records disappeared somewhere between the layers.

The project therefore uses reconciliation checks between stages and stores the results in:

```text
audit.recon_log
```

This is currently based primarily on record counts. It is deliberately simple, but it gives the pipeline an explicit data-quality checkpoint instead of relying only on task status.

## Why the generic layer matters

As we added more entities and pipeline stages, it became obvious that things like batch creation, database loading, archival, reconciliation and audit updates are **not really artist logic, release logic, or URL logic**.

They are pipeline concerns.

Instead of creating a separate version of the same logic for every table, the repository has a shared set of utilities under:

```text
generic_scripts/
```

These utilities are driven by values such as:

```text
source_system
phase_name
schema_name
table_name
group_name
etl_batch_id
```

For example, the same reconciliation concept can be used for:

```text
landing.lnd_artists
        ->
sanitised.san_artists
```

or:

```text
landing.lnd_releases
        ->
sanitised.san_releases
```

without changing the reconciliation implementation itself.

This is an important direction for the project.

If another source or another group of entities is added, the goal should be to **configure the existing framework**, not copy the framework and rename a few variables.

That separation also makes it easier for multiple engineers to work on the repository at the same time: source-specific work can evolve independently while common operational behavior stays shared.

## What we learned from the data itself

MusicBrainz also influenced the architecture.

The API returns nested JSON and relationships that are useful at the source level but inconvenient to query directly.

Rather than trying to fully normalize everything while making the API requests, we kept the landing layer close to the source:

```text
payload -> JSONB
```

This gives us a stable representation of what was actually received.

Transformation can then happen independently.

That separation turned out to be useful because it means:

- ingestion does not need to know the final analytical schema;
- transformations can be changed without repeatedly calling the source API;
- raw data can be inspected when debugging;
- the same source payload can support different downstream models.

This is one of the main reasons the project has a distinct Landing → Sanitized → Curated progression.

## Why Spark?

For a small MusicBrainz dataset, Spark is obviously more infrastructure than we strictly need.

That is intentional.

The project is also a learning environment for understanding how a pipeline changes when transformation logic moves from simple Python processing to distributed DataFrame-based processing.

Spark is currently used to parse the nested JSON stored in the landing layer and turn it into structured sanitized datasets.

The important lesson here is architectural rather than performance-driven:

> ingestion, transformation and orchestration do not need to be the same piece of code.

That separation gives us a structure that can grow beyond the current dataset size.

## Where the project is today

The current implementation has a working path around MusicBrainz artist, release and URL data:

```text
MusicBrainz
   ↓
Raw JSON
   ↓
Landing
   ↓
Spark cleansing
   ↓
Sanitized
   ↓
Curated artist/discography summary
```

Alongside this, the project has:

- Airflow orchestration
- PostgreSQL storage
- Spark-based transformations
- reusable batch utilities
- audit logging
- landing-to-sanitized reconciliation
- Docker-based local infrastructure

The codebase also contains work for additional entities and future pipeline paths. Not every defined table or script is currently part of the active end-to-end flow, and that is expected while the project is evolving.

## What we want to continue improving

The next step is less about adding random technologies and more about making the patterns we've learned stronger.

Some of the areas we want to continue with are:

- making source configuration more reusable;
- adding more entity groups without duplicating generic utilities;
- extending reconciliation beyond simple row counts;
- strengthening data-quality checks;
- completing additional MusicBrainz entities such as recordings;
- expanding the curated layer;
- improving configuration and secret management;
- adding meaningful automated tests;
- improving monitoring and failure visibility;
- making the local setup easier for another engineer to reproduce.

The long-term idea is to have a small but coherent ETL framework where a new pipeline can follow the same operational pattern without becoming a copy of an existing one.

## Repository structure

The repository is intentionally split between reusable pipeline components and source/domain-specific code:

```text
Music_Catalog_ETL/
│
├── airflow/
│   └── dags/                  # Workflow orchestration
│
├── ingestion/                # Source-specific extraction
│
├── generic_scripts/           # Shared ETL operational utilities
│
├── cleansing/                # Spark-based transformation logic
│
├── curation/                 # Analytical/curated transformations
│
├── sql/
│   ├── landing/              # Landing data model
│   ├── sanitised/            # Sanitized data model
│   ├── curated/              # Curated data model
│   └── audit/                # Batch and reconciliation model
│
├── data/
│   └── raw/                  # Persisted source payloads
│
├── configs/                  # Runtime/batch configuration
│
├── spark/                    # Spark runtime support
│
├── tests/                    # Tests and validation
│
├── docker-compose.local.yml
├── docker-compose.shared.yml
└── entrypoint.sh
```

A useful rule when extending the project is:

```text
If it describes the source -> source-specific package

If it describes how every pipeline should run -> generic_scripts

If it describes when things run -> Airflow

If it describes how data is shaped -> cleansing / curation

If it describes what data should look like -> SQL
```

## Running locally

The repository provides Docker Compose configurations for the local development environment.

```bash
docker compose -f docker-compose.local.yml up --build
```

The stack includes the services needed for the current development setup, including Airflow, PostgreSQL, Spark and pgAdmin.

The exact pipeline entry points and development commands can be found in the corresponding Airflow DAGs and project scripts.

## Project mindset

This repository is deliberately a learning project, but the problems we are trying to solve are real data engineering problems.

The useful outcome is not just a table containing MusicBrainz data.

It is understanding how to take a pipeline from:

```text
"the script works"
```

to:

```text
"the pipeline is repeatable,
the data can be traced,
the stages can be validated,
and the common pieces can be reused."
```

That is the foundation we want to continue building on.
