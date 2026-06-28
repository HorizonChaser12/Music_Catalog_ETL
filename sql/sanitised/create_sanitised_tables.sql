CREATE TABLE IF NOT EXISTS sanitised.san_artists(
    artist_id text PRIMARY KEY,
    name text NOT NULL,
    gender text,
    country text,
    score INTEGER,
    ingestion_date TIMESTAMP
);

