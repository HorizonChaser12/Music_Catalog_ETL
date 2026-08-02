CREATE TABLE IF NOT EXISTS sanitised.san_artists (
    artist_id TEXT,
    name TEXT NOT NULL,
    gender TEXT,
    country TEXT,
    type TEXT,
    area_id TEXT,
    area_name TEXT,
    etl_batch_id VARCHAR NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    CONSTRAINT pk_san_artists
        PRIMARY KEY (artist_id, etl_batch_id)
);

CREATE INDEX IF NOT EXISTS idx_san_artists_batch
ON sanitised.san_artists(etl_batch_id);


CREATE TABLE IF NOT EXISTS sanitised.san_releases (
    release_id VARCHAR,
    artist_id VARCHAR NOT NULL,
    title TEXT NOT NULL,
    status VARCHAR,
    release_date VARCHAR,
    country VARCHAR(5),
    barcode VARCHAR,
    track_count INTEGER,
    etl_batch_id VARCHAR NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    CONSTRAINT pk_san_releases
        PRIMARY KEY (release_id, etl_batch_id),
    CONSTRAINT fk_release_artist
        FOREIGN KEY (artist_id, etl_batch_id)
        REFERENCES sanitised.san_artists (artist_id, etl_batch_id)
);

CREATE INDEX IF NOT EXISTS idx_san_releases_batch
ON sanitised.san_releases(etl_batch_id);


CREATE TABLE IF NOT EXISTS sanitised.san_recordings (
    recording_id VARCHAR,
    release_id VARCHAR NOT NULL,
    track_id VARCHAR,
    track_position INTEGER,
    track_number INTEGER,
    recording_title TEXT,
    track_title TEXT,
    recording_length_ms INTEGER,
    first_release_date VARCHAR,
    is_video BOOLEAN,
    etl_batch_id VARCHAR NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    CONSTRAINT pk_san_recordings
        PRIMARY KEY (recording_id, etl_batch_id),
    CONSTRAINT fk_recordings_release
        FOREIGN KEY (release_id, etl_batch_id)
        REFERENCES sanitised.san_releases (release_id, etl_batch_id)
);

CREATE INDEX IF NOT EXISTS idx_san_recordings_batch
ON sanitised.san_recordings(etl_batch_id);