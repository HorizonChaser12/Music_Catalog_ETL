-- sql/landing/create_landing_tables.sql

CREATE TABLE IF NOT EXISTS lnd_artists (
    ingestion_id SERIAL PRIMARY KEY,
    ingestion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payload JSONB
);

CREATE TABLE IF NOT EXISTS lnd_releases (
    ingestion_id SERIAL PRIMARY KEY,
    ingestion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payload JSONB
);

CREATE TABLE IF NOT EXISTS lnd_recordings (
    ingestion_id SERIAL PRIMARY KEY,
    ingestion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payload JSONB
);

CREATE TABLE IF NOT EXISTS lnd_urls (
    ingestion_id SERIAL PRIMARY KEY,
    ingestion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payload JSONB
);