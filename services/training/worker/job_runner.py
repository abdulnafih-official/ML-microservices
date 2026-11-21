import logging
import time

import pandas as pd
from sqlalchemy import text

from mlp_common.metrics import llm_plan_total, training_jobs_total, training_duration_seconds

from app.auth_client import release_quota
from app.config import Settings
from app.db import SessionLocal
from app.upload import delete_upload
from .compiler import build_pipeline, feature_schema
from .evaluate import compute_metrics, split_data
from .hf_store import upload_model
from .metadata import write_model_metadata
from .planner.gemini import GeminiPlanner, PlannerError
from .planner.rules import RulesPlanner
from .profiler import profile_dataframe
from .trainers import get_estimator
from .validator import apply_hard_rules, validate_plan


def obtain_plan(profile: dict, task_type: str, target: str, ai_cleaning: bool):
    settings = Settings()
    if ai_cleaning:
        try:
            raw = GeminiPlanner(settings.GEMINI_API_KEY, settings.GEMINI_MODEL).plan(profile, task_type, target)
            plan = validate_plan(raw, list(profile["columns"]), target)
            llm_plan_total.labels(outcome="success").inc()
            return apply_hard_rules(plan, profile), "llm", False
        except (PlannerError, Exception) as exc:
            llm_plan_total.labels(outcome="fallback").inc()
            logging.getLogger(__name__).warning("LLM plan unavailable: %s", exc)
    raw = RulesPlanner().plan(profile, task_type, target)
    plan = validate_plan(raw, list(profile["columns"]), target)
    return apply_hard_rules(plan, profile), "rules", ai_cleaning


def mark_succeeded(job_id, model_id) -> None:
    with SessionLocal() as db:
        db.execute(text("UPDATE training.jobs SET status='succeeded', error=NULL WHERE id=:id"),
                   {"id": job_id})
        db.commit()


def mark_failed(job_id, user_id, error: str) -> None:
    with SessionLocal() as db:
        db.execute(text("UPDATE training.jobs SET status='failed', error=:error WHERE id=:id"),
                   {"id": job_id, "error": error[:2000]})
        db.commit()
    try:
        release_quota(user_id)
    except Exception:
        logging.getLogger(__name__).exception("Could not release training quota")
    training_jobs_total.labels(status="failed").inc()


def run_job(job) -> None:
    started = time.monotonic()
    payload = job["payload"]
    path = payload["file_path"]
    try:
        df = pd.read_csv(path)
        df = df.dropna(subset=[payload["target_col"]])
        profile = profile_dataframe(df, payload["target_col"], payload["task_type"])
        plan, plan_source, fallback_used = obtain_plan(
            profile, payload["task_type"], payload["target_col"], payload["ai_cleaning"]
        )
        X_train, X_test, y_train, y_test = split_data(df, payload["target_col"], payload["task_type"])
        estimator = get_estimator(payload["algo"], payload["task_type"])
        pipeline = build_pipeline(plan, estimator)
        pipeline.fit(X_train, y_train)
        metrics = compute_metrics(pipeline, X_test, y_test, payload["task_type"])
        hf_path, hf_revision = upload_model(pipeline, str(job["user_id"]), str(job["id"]))
        with SessionLocal() as db:
            model_id = write_model_metadata(
                db, job, plan, plan_source, fallback_used, profile, metrics,
                feature_schema(plan, df), hf_path, hf_revision,
            )
        mark_succeeded(job["id"], model_id)
        training_jobs_total.labels(status="succeeded").inc()
        training_duration_seconds.observe(time.monotonic() - started)
    except Exception as exc:
        logging.getLogger(__name__).exception("Training job failed")
        mark_failed(job["id"], job["user_id"], str(exc))
    finally:
        delete_upload(path)
