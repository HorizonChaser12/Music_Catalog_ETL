-- Landing tables schema with id, payload, created_at, updated_at columns

CREATE TABLE IF NOT EXISTS landing.lnd_artists (
    id UUID PRIMARY KEY,
    payload JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS landing.lnd_releases (
    id UUID PRIMARY KEY,
    payload JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS landing.lnd_recordings (
    id UUID PRIMARY KEY,
    payload JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS landing.lnd_urls (
    id UUID PRIMARY KEY,
    payload JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS landing.lnd_release_groups (
    id UUID PRIMARY KEY,
    payload JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes on updated_at for efficient querying
CREATE INDEX IF NOT EXISTS idx_lnd_artists_updated_at ON landing.lnd_artists(updated_at);
CREATE INDEX IF NOT EXISTS idx_lnd_releases_updated_at ON landing.lnd_releases(updated_at);
CREATE INDEX IF NOT EXISTS idx_lnd_recordings_updated_at ON landing.lnd_recordings(updated_at);
CREATE INDEX IF NOT EXISTS idx_lnd_urls_updated_at ON landing.lnd_urls(updated_at);
CREATE INDEX IF NOT EXISTS idx_lnd_release_groups_updated_at ON landing.lnd_release_groups(updated_at);