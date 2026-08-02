CREATE SCHEMA IF NOT EXISTS curated;

CREATE TABLE IF NOT EXISTS curated.cur_artist_track_summary (
    artist_id VARCHAR,
    artist_name TEXT,
    total_tracks BIGINT
);

ALTER TABLE curated.cur_artist_track_summary
    ADD COLUMN IF NOT EXISTS etl_batch_id VARCHAR,
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_cur_artist_track_summary_batch
ON curated.cur_artist_track_summary(etl_batch_id);

CREATE TABLE IF NOT EXISTS curated.cur_artist_release_summary (
    artist_id VARCHAR,
    artist_name TEXT,
    total_releases BIGINT
);

ALTER TABLE curated.cur_artist_release_summary
    ADD COLUMN IF NOT EXISTS etl_batch_id VARCHAR,
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_cur_artist_release_summary_batch
ON curated.cur_artist_release_summary(etl_batch_id);

CREATE TABLE IF NOT EXISTS curated.cur_artist_duration_summary (
    artist_id VARCHAR,
    artist_name TEXT,
    total_tracks INTEGER,
    average_track_length_ms NUMERIC(10,2),
    longest_track_ms INTEGER,
    shortest_track_ms INTEGER
);

ALTER TABLE curated.cur_artist_duration_summary
    ADD COLUMN IF NOT EXISTS etl_batch_id VARCHAR,
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_cur_artist_duration_summary_batch
ON curated.cur_artist_duration_summary(etl_batch_id);

CREATE TABLE IF NOT EXISTS curated.cur_release_year_summary (
    release_year INTEGER NOT NULL,
    total_releases BIGINT
);

ALTER TABLE curated.cur_release_year_summary
    ADD COLUMN IF NOT EXISTS etl_batch_id VARCHAR,
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_cur_release_year_summary_batch
ON curated.cur_release_year_summary(etl_batch_id);

CREATE TABLE IF NOT EXISTS curated.cur_artist_top_tracks (
    recording_id VARCHAR,
    artist_id VARCHAR,
    artist_name TEXT,
    release_title TEXT,
    track_title TEXT,
    recording_length_ms INTEGER,
    track_rank INTEGER
);

ALTER TABLE curated.cur_artist_top_tracks
    ADD COLUMN IF NOT EXISTS etl_batch_id VARCHAR,
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_cur_artist_top_tracks_batch
ON curated.cur_artist_top_tracks(etl_batch_id);