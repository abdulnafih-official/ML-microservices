import os
import shutil
import uuid

import pandas as pd
from fastapi import HTTPException, UploadFile

from .config import Settings


def validate_and_store(file: UploadFile, target_col: str) -> str:
    settings = Settings()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    path = os.path.join(settings.UPLOAD_DIR, f"{uuid.uuid4()}.csv")
    total = 0
    with open(path, "wb") as out:
        while chunk := file.file.read(1024 * 1024):
            total += len(chunk)
            if total > settings.MAX_UPLOAD_MB * 1024 * 1024:
                out.close()
                os.remove(path)
                raise HTTPException(status_code=413, detail="Upload exceeds size limit")
            out.write(chunk)
    try:
        df = pd.read_csv(path)
    except Exception as exc:
        os.remove(path)
        raise HTTPException(status_code=400, detail="Invalid CSV") from exc
    if len(df) > settings.MAX_ROWS:
        os.remove(path)
        raise HTTPException(status_code=400, detail=f"CSV exceeds {settings.MAX_ROWS} rows")
    if target_col not in df.columns:
        os.remove(path)
        raise HTTPException(status_code=422, detail=f"Target column '{target_col}' not found")
    return path


def delete_upload(path: str) -> None:
    if path and os.path.isfile(path):
        os.remove(path)
