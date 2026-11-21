import numpy as np
from fastapi import APIRouter, Depends, Header, HTTPException

from mlp_common.jwt_utils import verify_token

from ..cache import get_pipeline
from ..config import Settings
from ..db import get_db
from ..input_validation import validate_payload
from ..registry import get_model

router = APIRouter(prefix="/predict", tags=["predict"])
settings = Settings()


def current_user_id(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization required")
    payload = verify_token(authorization.removeprefix("Bearer ").strip(), settings.JWT_SECRET)
    return payload["sub"]


@router.post("/{model_id}")
def predict(model_id: str, payload: dict, user_id: str = Depends(current_user_id), db=Depends(get_db)):
    model = get_model(db, model_id, user_id)
    frame = validate_payload(payload, model["feature_schema"])
    pipeline = get_pipeline(model)
    prediction = pipeline.predict(frame)
    result = {"prediction": prediction[0].item() if hasattr(prediction[0], "item") else prediction[0]}
    if model["task_type"] == "classification" and hasattr(pipeline, "predict_proba"):
        probabilities = pipeline.predict_proba(frame)[0]
        estimator = pipeline.named_steps.get("estimator")
        classes = getattr(estimator, "classes_", list(range(len(probabilities))))
        result["probabilities"] = {
            str(label): float(prob) for label, prob in zip(classes, probabilities)
        }
    return result
