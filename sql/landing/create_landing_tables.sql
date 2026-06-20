-- Landing tables schema with id, payload, created_at, updated_at columns

CREATE TABLE IF NOT EXISTS lnd_artists (
    id BIGINT PRIMARY KEY,
    payload JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lnd_releases (
    id BIGINT PRIMARY KEY,
    payload JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lnd_recordings (
    id BIGINT PRIMARY KEY,
    payload JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lnd_urls (
    id BIGINT PRIMARY KEY,
    payload JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes on updated_at for efficient querying
CREATE INDEX IF NOT EXISTS idx_lnd_artists_updated_at ON lnd_artists(updated_at);
CREATE INDEX IF NOT EXISTS idx_lnd_releases_updated_at ON lnd_releases(updated_at);
CREATE INDEX IF NOT EXISTS idx_lnd_recordings_updated_at ON lnd_recordings(updated_at);
CREATE INDEX IF NOT EXISTS idx_lnd_urls_updated_at ON lnd_urls(updated_at);