import time
from datetime import datetime, timedelta, timezone
from typing import Any

from prometheus_client import start_http_server
from sqlalchemy import text

from mlp_common.metrics import training_queue_length

from app.auth_client import release_quota
from app.config import Settings
from app.db import engine
from .job_runner import run_job


def row_to_job(row) -> dict[str, Any]:
    return {"id": row.id, "user_id": row.user_id, "payload": row.payload,
            "status": row.status, "attempts": row.attempts}


def claim_job(conn) -> dict | None:
    row = conn.execute(text("""
        UPDATE training.jobs
        SET status='running', attempts=attempts+1, locked_at=NOW()
        WHERE id = (
            SELECT id FROM training.jobs
            WHERE status='queued'
            ORDER BY created_at
            FOR UPDATE SKIP LOCKED
            LIMIT 1
        )
        RETURNING id,user_id,payload,status,attempts
    """)).first()
    conn.commit()
    return row_to_job(row) if row else None


def reap_stuck_jobs(conn) -> None:
    settings = Settings()
    cutoff = datetime.now(tz=timezone.utc) - timedelta(minutes=settings.JOB_TIMEOUT_MINUTES)
    rows = conn.execute(text("""
        SELECT id,user_id,attempts FROM training.jobs
        WHERE status='running' AND locked_at IS NOT NULL AND locked_at < :cutoff
    """), {"cutoff": cutoff}).all()
    for row in rows:
        if row.attempts < settings.MAX_JOB_ATTEMPTS:
            conn.execute(text("""
                UPDATE training.jobs SET status='queued', locked_at=NULL
                WHERE id=:id
            """), {"id": row.id})
        else:
            conn.execute(text("""
                UPDATE training.jobs SET status='failed', error='Job timed out',
                locked_at=NULL WHERE id=:id
            """), {"id": row.id})
            release_quota(row.user_id)
    conn.commit()


def update_queue_length(conn) -> None:
    count = conn.execute(text("""
        SELECT COUNT(*) FROM training.jobs WHERE status='queued'
    """)).scalar_one()
    training_queue_length.set(count)


def run_loop() -> None:
    start_http_server(8001)
    while True:
        with engine.begin() as conn:
            reap_stuck_jobs(conn)
            update_queue_length(conn)
            job = claim_job(conn)
        if job:
            run_job(job)
        else:
            time.sleep(2)


if __name__ == "__main__":
    run_loop()
