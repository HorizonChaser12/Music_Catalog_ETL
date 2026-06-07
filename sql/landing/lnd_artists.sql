CREATE TABLE IF NOT EXISTS lnd_artists(
    ingestion_id SERIAL PRIMARY KEY,
    ingestion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payload JSONB
)
