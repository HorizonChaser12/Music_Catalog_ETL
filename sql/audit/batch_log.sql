-- Batch Log Table for ETL Auditing
CREATE TABLE IF NOT EXISTS batch_log (
    etl_batch_id VARCHAR(255) NOT NULL,
    phase_name VARCHAR(100) NOT NULL,
    source_system VARCHAR(100) NOT NULL,
    batch_status CHAR(1) NOT NULL DEFAULT 'S' CHECK (batch_status IN ('S', 'C', 'E')),
    record_count_processed INTEGER DEFAULT 0,
    record_count_failed INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_batch_phase_source UNIQUE (etl_batch_id, phase_name, source_system)
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_batch_log_etl_batch_id ON audit.batch_log(etl_batch_id);
CREATE INDEX IF NOT EXISTS idx_batch_log_phase ON audit.batch_log(phase_name);
CREATE INDEX IF NOT EXISTS idx_batch_log_source ON audit.batch_log(source_system);
CREATE INDEX IF NOT EXISTS idx_batch_log_status ON audit.batch_log(batch_status);
