CREATE TABLE IF NOT EXISTS curated.cur_artist_track_summary (
    artist_id VARCHAR PRIMARY KEY,
    artist_name TEXT,
    total_tracks BIGINT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS curated.cur_artist_release_summary (
    artist_id VARCHAR PRIMARY KEY,
    artist_name TEXT,
    total_releases BIGINT,
    created_at TIMESTAMP
);