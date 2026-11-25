import pandas as pd
from fastapi import APIRouter, Depends, Header, HTTPException

from mlp_common.jwt_utils import verify_token

from ..cache import get_pipeline
from ..config import Settings
from ..db import get_db
from ..input_validation import validate_batch_payload, validate_payload
from ..registry import get_model

router = APIRouter(prefix="/predict", tags=["predict"])
settings = Settings()


def current_user_id(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization required")
    payload = verify_token(authorization.removeprefix("Bearer ").strip(), settings.JWT_SECRET)
    return payload["sub"]


def predict_frame(model: dict, frame: pd.DataFrame, pipeline) -> list[dict]:
    predictions = pipeline.predict(frame)
    results = [
        {"prediction": value.item() if hasattr(value, "item") else value}
        for value in predictions
    ]
    if model["task_type"] == "classification" and hasattr(pipeline, "predict_proba"):
        probabilities = pipeline.predict_proba(frame)
        estimator = pipeline.named_steps.get("estimator")
        classes = getattr(estimator, "classes_", list(range(len(probabilities[0]))))
        for result, row in zip(results, probabilities):
            result["probabilities"] = {
                str(label): float(prob) for label, prob in zip(classes, row)
            }
    return results


@router.post("/{model_id}")
def predict(model_id: str, payload: dict, user_id: str = Depends(current_user_id), db=Depends(get_db)):
    model = get_model(db, model_id, user_id)
    frame = validate_payload(payload, model["feature_schema"])
    pipeline = get_pipeline(model)
    return predict_frame(model, frame, pipeline)[0]


@router.post("/{model_id}/batch")
def predict_batch(
    model_id: str,
    payload: list[dict],
    user_id: str = Depends(current_user_id),
    db=Depends(get_db),
):
    model = get_model(db, model_id, user_id)
    frame = validate_batch_payload(payload, model["feature_schema"], settings.MAX_BATCH_PREDICTIONS)
    pipeline = get_pipeline(model)
    return {"results": predict_frame(model, frame, pipeline)}
