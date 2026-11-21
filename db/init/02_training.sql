CREATE SCHEMA IF NOT EXISTS training;

CREATE TABLE IF NOT EXISTS training.jobs (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    payload JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    attempts INTEGER NOT NULL DEFAULT 0,
    locked_at TIMESTAMPTZ,
    error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS jobs_status_created_idx
    ON training.jobs(status, created_at);
