from fastapi import APIRouter, Depends, Header, HTTPException

from mlp_common.jwt_utils import verify_token

from ..config import Settings
from ..db import get_db
from ..registry import get_model, list_models

router = APIRouter(prefix="/models", tags=["models"])
settings = Settings()


def current_user_id(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization required")
    payload = verify_token(authorization.removeprefix("Bearer ").strip(), settings.JWT_SECRET)
    return payload["sub"]


@router.get("")
def models(user_id: str = Depends(current_user_id), db=Depends(get_db)):
    return list_models(db, user_id)


@router.get("/{model_id}")
def model_detail(model_id: str, user_id: str = Depends(current_user_id), db=Depends(get_db)):
    return get_model(db, model_id, user_id)
