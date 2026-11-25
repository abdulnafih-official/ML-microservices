import pandas as pd
from fastapi import HTTPException


def validate_payload(payload: dict, feature_schema: dict) -> pd.DataFrame:
    if not isinstance(payload, dict):
        raise HTTPException(status_code=422, detail="Payload must be a JSON object")
    missing = [name for name in feature_schema if name not in payload]
    extra = [name for name in payload if name not in feature_schema]
    if missing:
        raise HTTPException(status_code=422, detail=f"Missing fields: {', '.join(missing)}")
    if extra:
        raise HTTPException(status_code=422, detail=f"Extra fields: {', '.join(extra)}")
    row = {}
    for name in feature_schema:
        expected = feature_schema[name]
        value = payload[name]
        if expected == "number":
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise HTTPException(status_code=422, detail=f"Field '{name}' must be a number")
            row[name] = float(value)
        elif expected == "string":
            if not isinstance(value, str):
                raise HTTPException(status_code=422, detail=f"Field '{name}' must be a string")
            row[name] = value
        else:
            row[name] = value
    return pd.DataFrame([row], columns=list(feature_schema.keys()))


def validate_batch_payload(payload: list, feature_schema: dict, max_rows: int) -> pd.DataFrame:
    if not isinstance(payload, list) or not payload:
        raise HTTPException(status_code=422, detail="Payload must be a non-empty JSON array")
    if len(payload) > max_rows:
        raise HTTPException(status_code=413, detail=f"Batch exceeds the {max_rows}-row limit")

    frames = []
    for index, row in enumerate(payload, start=1):
        try:
            frames.append(validate_payload(row, feature_schema))
        except HTTPException as exc:
            raise HTTPException(status_code=exc.status_code, detail=f"Row {index}: {exc.detail}") from exc
    return pd.concat(frames, ignore_index=True)
