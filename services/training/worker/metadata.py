from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import text


def write_model_metadata(db, job, plan, plan_source: str, fallback_used: bool, profile: dict,
                         metrics: dict, feature_schema: dict, hf_path: str, hf_revision: str):
    model_id = uuid4()
    payload = job["payload"] if isinstance(job, dict) else job.payload
    if hasattr(payload, "dict"):
        payload = payload.dict()
    db.execute(text("""
        INSERT INTO models.models (
            id,user_id,name,algo,task_type,target_col,feature_schema,metrics,profile_summary,
            cleaning_plan,plan_source,fallback_used,hf_repo,hf_path,hf_revision,status,created_at
        ) VALUES (
            :id,:user_id,:name,:algo,:task_type,:target_col,CAST(:feature_schema AS JSONB),
            CAST(:metrics AS JSONB),CAST(:profile_summary AS JSONB),CAST(:cleaning_plan AS JSONB),
            :plan_source,:fallback_used,:hf_repo,:hf_path,:hf_revision,'ready',:created_at
        )
    """), {
        "id": model_id,
        "user_id": job["user_id"],
        "name": f"{payload['algo']}-{model_id}",
        "algo": payload["algo"],
        "task_type": payload["task_type"],
        "target_col": payload["target_col"],
        "feature_schema": __import__("json").dumps(feature_schema),
        "metrics": __import__("json").dumps(metrics),
        "profile_summary": __import__("json").dumps(profile),
        "cleaning_plan": __import__("json").dumps(plan.model_dump(mode="json")),
        "plan_source": plan_source,
        "fallback_used": fallback_used,
        "hf_repo": __import__("os").environ.get("HF_REPO_ID", ""),
        "hf_path": hf_path,
        "hf_revision": hf_revision,
        "created_at": datetime.now(tz=timezone.utc),
    })
    db.execute(text("""
        UPDATE auth.users
        SET models_trained=models_trained+1,
            models_reserved=GREATEST(models_reserved-1,0)
        WHERE id=:id
    """),
               {"id": job["user_id"]})
    db.commit()
    return model_id
