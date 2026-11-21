import json
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile
from sqlalchemy import text

from mlp_common.jwt_utils import verify_token

from ..auth_client import release_quota, reserve_quota
from ..config import Settings
from ..db import get_db
from ..schemas import Algo, JobOut, TaskType
from ..upload import delete_upload, validate_and_store

router = APIRouter(tags=["jobs"])
settings = Settings()


def current_user_id(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization required")
    payload = verify_token(authorization.removeprefix("Bearer ").strip(), settings.JWT_SECRET)
    return payload["sub"]


@router.post("/train", response_model=JobOut)
async def train(
    file: UploadFile = File(...),
    algo: Algo = Form(...),
    task_type: TaskType = Form(...),
    target_col: str = Form(...),
    ai_cleaning: bool = Form(True),
    user_id: str = Depends(current_user_id),
    db=Depends(get_db),
):
    if not reserve_quota(user_id):
        raise HTTPException(status_code=403, detail="Model quota exceeded")
    path = None
    try:
        path = validate_and_store(file, target_col)
        job_id = uuid4()
        payload = {
            "algo": algo.value,
            "task_type": task_type.value,
            "target_col": target_col,
            "ai_cleaning": ai_cleaning,
            "file_path": path,
        }
        db.execute(text("""
            INSERT INTO training.jobs(id,user_id,payload,status,attempts,created_at)
            VALUES (:id,:user_id,CAST(:payload AS JSONB),'queued',0,NOW())
        """), {"id": job_id, "user_id": user_id, "payload": json.dumps(payload)})
        db.commit()
        row = db.execute(text("""
            SELECT id,status,error,created_at FROM training.jobs WHERE id=:id
        """), {"id": job_id}).mappings().first()
        return JobOut(id=row["id"], status=row["status"], error=row["error"],
                      created_at=row["created_at"], model_id=None)
    except Exception as exc:
        db.rollback()
        if path:
            delete_upload(path)
        release_quota(user_id)
        if isinstance(exc, HTTPException):
            raise
        raise HTTPException(status_code=500, detail="Could not create training job") from exc


@router.get("/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: str, user_id: str = Depends(current_user_id), db=Depends(get_db)):
    row = db.execute(text("""
        SELECT j.id,j.status,j.error,j.created_at,m.id AS model_id
        FROM training.jobs j
        LEFT JOIN models.models m ON m.id = (
            SELECT id FROM models.models
            WHERE user_id=CAST(j.user_id AS UUID)
              AND created_at >= j.created_at
            ORDER BY created_at DESC LIMIT 1
        )
        WHERE j.id=:job_id AND j.user_id=:user_id
    """), {"job_id": job_id, "user_id": user_id}).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobOut(id=row["id"], status=row["status"], error=row["error"],
                  created_at=row["created_at"], model_id=row["model_id"])


@router.get("/jobs", response_model=list[JobOut])
def list_jobs(user_id: str = Depends(current_user_id), db=Depends(get_db)):
    rows = db.execute(text("""
        SELECT id,status,error,created_at
        FROM training.jobs
        WHERE user_id=:user_id
        ORDER BY created_at DESC
    """), {"user_id": user_id}).mappings().all()
    return [JobOut(id=r["id"], status=r["status"], error=r["error"],
                   created_at=r["created_at"], model_id=None) for r in rows]
