CREATE TABLE IF NOT EXISTS san_artists(
    artist_id text PRIMARY KEY,
    name text NOT NULL,
    gendet text,
    country text,
    score INTEGER,
    ingestion_date TIMESTAMP
);

