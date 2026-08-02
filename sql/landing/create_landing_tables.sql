CREATE TABLE IF NOT EXISTS landing.lnd_artists (
    id UUID NOT NULL,
    payload JSONB NOT NULL,
    etl_batch_id VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, etl_batch_id)
);

CREATE INDEX IF NOT EXISTS idx_lnd_artists_batch
ON landing.lnd_artists(etl_batch_id);



CREATE TABLE IF NOT EXISTS landing.lnd_releases (
    id UUID NOT NULL,
    queried_artist_id UUID,
    payload JSONB NOT NULL,
    etl_batch_id VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, etl_batch_id)
);

CREATE INDEX IF NOT EXISTS idx_lnd_releases_batch
ON landing.lnd_releases(etl_batch_id);



CREATE TABLE IF NOT EXISTS landing.lnd_recordings (
    id UUID NOT NULL,
    payload JSONB NOT NULL,
    etl_batch_id VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, etl_batch_id)
);

CREATE INDEX IF NOT EXISTS idx_lnd_recordings_batch
ON landing.lnd_recordings(etl_batch_id);



CREATE TABLE IF NOT EXISTS landing.lnd_urls (
    id UUID NOT NULL,
    payload JSONB NOT NULL,
    etl_batch_id VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, etl_batch_id)
);

CREATE INDEX IF NOT EXISTS idx_lnd_urls_batch
ON landing.lnd_urls(etl_batch_id);