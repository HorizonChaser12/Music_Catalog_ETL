CREATE TABLE IF NOT EXISTS sanitised.san_artists(
    artist_id text PRIMARY KEY,
    name text NOT NULL,
    gender text,
    country text,
    type text,
    area_id text,
    area_name text,
    created_at TIMESTAMP,
    updated_At TIMESTAMP
)
