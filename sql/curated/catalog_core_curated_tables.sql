CREATE TABLE curated.cur_artist_discography_summary (
    artist_id           TEXT     NOT NULL,
    artist_name         VARCHAR(255),
    total_releases      INTEGER,
    distinct_release_groups INTEGER,
    avg_track_count     NUMERIC(6,2),
    earliest_release_date DATE,
    latest_release_date DATE,
    created_at          TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    etl_batch_id        VARCHAR(50),

    CONSTRAINT pk_cur_artist_discography_summary PRIMARY KEY (artist_id)
);