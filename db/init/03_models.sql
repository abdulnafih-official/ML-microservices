CREATE SCHEMA IF NOT EXISTS models;

CREATE TABLE IF NOT EXISTS models.models (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    name TEXT NOT NULL,
    algo TEXT NOT NULL,
    task_type TEXT NOT NULL,
    target_col TEXT NOT NULL,
    feature_schema JSONB NOT NULL,
    metrics JSONB NOT NULL,
    profile_summary JSONB NOT NULL,
    cleaning_plan JSONB NOT NULL,
    plan_source TEXT NOT NULL,
    fallback_used BOOLEAN NOT NULL DEFAULT FALSE,
    hf_repo TEXT NOT NULL,
    hf_path TEXT NOT NULL,
    hf_revision TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ready',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS models_user_created_idx
    ON models.models(user_id, created_at DESC);
