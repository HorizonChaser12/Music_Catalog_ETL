-- ============================================================
-- sanitised.san_artists  (15 columns)
-- ============================================================
CREATE TABLE IF NOT EXISTS sanitised.san_artists (
    artist_id        TEXT PRIMARY KEY,
    artist_name      TEXT,
    sort_name        TEXT,
    gender           TEXT,
    country          TEXT,
    type             TEXT,
    disambiguation   TEXT,
    area_id          TEXT,
    area_name        TEXT,
    life_span_begin  TEXT,
    life_span_end    TEXT,
    life_span_ended  TEXT,
    created_at       TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    etl_batch_id     TEXT
);

-- ============================================================
-- sanitised.san_releases  (20 columns)
-- ============================================================
CREATE TABLE IF NOT EXISTS sanitised.san_releases (
    release_id          TEXT PRIMARY KEY,
    release_title       TEXT,
    release_status      TEXT,
    release_date        TEXT,
    release_country     TEXT,
    barcode             TEXT,
    artist_id           TEXT,
    artist_name         TEXT,
    release_group_id    TEXT,
    release_group_title TEXT,
    release_group_type  TEXT,
    area_id             TEXT,
    area_name           TEXT,
    label_id            TEXT,
    label_name          TEXT,
    format              TEXT,
    track_count         TEXT,
    created_at          TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    etl_batch_id        TEXT
);

-- ============================================================
-- sanitised.san_urls  (7 columns)
-- ============================================================
CREATE TABLE IF NOT EXISTS sanitised.san_urls (
    url_id       TEXT PRIMARY KEY,
    url          TEXT,
    url_type     TEXT,
    domain       TEXT,
    created_at   TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    etl_batch_id TEXT
);