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
);

CREATE TABLE IF NOT EXISTS sanitised.san_releases(
    release_id VARCHAR PRIMARY KEY,
    artist_id VARCHAR NOT NULL,
    title TEXT NOT NULL,
    status VARCHAR,
    release_date VARCHAR,
    country VARCHAR(5),
    barcode VARCHAR,
    track_count INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    CONSTRAINT fk_release_artist
        FOREIGN KEY (artist_id)
        REFERENCES sanitised.san_artists(artist_id)
);
CREATE TABLE IF NOT EXISTS sanitised.san_recordings(
    recording_id VARCHAR PRIMARY KEY,
    release_id VARCHAR NOT NULL,
    track_id VARCHAR,
    track_position INTEGER,
    track_number INTEGER,
    recording_title TEXT,
    track_title TEXT,
    recording_length_ms INTEGER,
    first_release_date VARCHAR,
    is_video BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    CONSTRAINT fk_recordings_release
        FOREIGN KEY (release_id)
        REFERENCES sanitised.san_releases(release_id)
);