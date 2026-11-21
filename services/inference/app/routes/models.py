from fastapi import APIRouter, Depends, Header, HTTPException, Response
from huggingface_hub.errors import HfHubHTTPError
from sqlalchemy import text

from mlp_common.jwt_utils import verify_token

from ..config import Settings
from ..db import get_db
from ..cache import remove_cached_model
from ..hf_loader import delete_model_file
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


@router.delete("/{model_id}", status_code=204)
def delete_model(model_id: str, user_id: str = Depends(current_user_id), db=Depends(get_db)):
    model = get_model(db, model_id, user_id)
    try:
        delete_model_file(model["hf_repo"], model["hf_path"])
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except HfHubHTTPError as exc:
        raise HTTPException(status_code=502, detail="Could not delete model artifact from Hugging Face") from exc

    try:
        db.execute(text("DELETE FROM models.models WHERE id=:id"), {"id": model_id})
        db.execute(text("""
            UPDATE auth.users
            SET models_trained=GREATEST(models_trained-1,0)
            WHERE id=:user_id
        """), {"user_id": user_id})
        db.commit()
    except Exception:
        db.rollback()
        raise
    remove_cached_model(model_id)
    return Response(status_code=204)
