from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import text


def list_models(db, user_id: str) -> list:
    rows = db.execute(text("""
        SELECT id,user_id,name,algo,task_type,target_col,feature_schema,metrics,
               profile_summary,cleaning_plan,plan_source,fallback_used,hf_repo,
               hf_path,hf_revision,status,created_at
        FROM models.models
        WHERE user_id=:user_id
        ORDER BY created_at DESC
    """), {"user_id": user_id}).mappings().all()
    return [dict(row) for row in rows]


def get_model(db, model_id: str, user_id: str) -> dict:
    row = db.execute(text("""
        SELECT id,user_id,name,algo,task_type,target_col,feature_schema,metrics,
               profile_summary,cleaning_plan,plan_source,fallback_used,hf_repo,
               hf_path,hf_revision,status,created_at
        FROM models.models
        WHERE id=:model_id
    """), {"model_id": model_id}).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Model not found")
    if str(row["user_id"]) != str(user_id):
        raise HTTPException(status_code=403, detail="Not the owner of this model")
    return dict(row)
