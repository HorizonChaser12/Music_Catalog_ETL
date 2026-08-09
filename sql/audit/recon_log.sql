-- Reconciliation Log Table for ETL Auditing
CREATE TABLE IF NOT EXISTS audit.recon_log (
    etl_batch_id VARCHAR(255) NOT NULL,
    phase_name VARCHAR(100) NOT NULL,
    source_system VARCHAR(100) NOT NULL,

    recon_status CHAR(1) NOT NULL DEFAULT 'S'
        CHECK (recon_status IN ('S', 'C', 'E')),

    record_count_processed INTEGER DEFAULT 0,
    record_count_failed INTEGER DEFAULT 0,

    source_table VARCHAR(255) NOT NULL,
    target_table VARCHAR(255) NOT NULL,
    group_name VARCHAR(255) NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

   CONSTRAINT unique_recon_batch_phase_source_group_table
    UNIQUE (
    etl_batch_id,
    phase_name,
    source_system,
    group_name,
    source_table,
    target_table
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_recon_log_etl_batch_id
    ON audit.recon_log(etl_batch_id);

CREATE INDEX IF NOT EXISTS idx_recon_log_phase
    ON audit.recon_log(phase_name);

CREATE INDEX IF NOT EXISTS idx_recon_log_source
    ON audit.recon_log(source_system);

CREATE INDEX IF NOT EXISTS idx_recon_log_status
    ON audit.recon_log(recon_status);

CREATE INDEX IF NOT EXISTS idx_recon_log_group_name
    ON audit.recon_log(group_name);

CREATE INDEX IF NOT EXISTS idx_recon_log_source_table
    ON audit.recon_log(source_table);

CREATE INDEX IF NOT EXISTS idx_recon_log_target_table
    ON audit.recon_log(target_table);