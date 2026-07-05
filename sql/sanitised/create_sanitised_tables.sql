CREATE TABLE IF NOT EXISTS san_artists(
    artist_id text PRIMARY KEY,
    name text NOT NULL,
    gendet text,
    country text,
    type text,
    area_id text,
    area_name text,
    created_at TIMESTAMP,
    updated_At TIMESTAMP
)
