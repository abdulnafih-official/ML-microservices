from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from mlp_common.metrics import quota_rejections_total

from ..config import Settings
from ..db import get_db
from ..quota import get_usage, release_slot, reserve_slot
from ..schemas import QuotaRequest, QuotaResponse

router = APIRouter(prefix="/internal", tags=["internal"])
settings = Settings()


def require_internal_key(x_internal_key: str | None = Header(default=None)) -> None:
    if x_internal_key != settings.INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid internal API key")


@router.post("/quota/reserve", response_model=QuotaResponse)
def reserve(payload: QuotaRequest, db: Session = Depends(get_db), _=Depends(require_internal_key)):
    allowed = reserve_slot(db, payload.user_id, settings.FREE_MODEL_LIMIT)
    if not allowed:
        quota_rejections_total.inc()
        used, limit = get_usage(db, payload.user_id, settings.FREE_MODEL_LIMIT)
        raise HTTPException(status_code=403, detail=QuotaResponse(
            allowed=False, used=used, limit=limit
        ).model_dump())
    used, limit = get_usage(db, payload.user_id, settings.FREE_MODEL_LIMIT)
    return QuotaResponse(allowed=True, used=used, limit=limit)


@router.post("/quota/release", response_model=QuotaResponse)
def release(payload: QuotaRequest, db: Session = Depends(get_db), _=Depends(require_internal_key)):
    release_slot(db, payload.user_id)
    used, limit = get_usage(db, payload.user_id, settings.FREE_MODEL_LIMIT)
    return QuotaResponse(allowed=True, used=used, limit=limit)
