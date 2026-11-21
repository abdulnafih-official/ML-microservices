import os
import tempfile
import uuid

import joblib
from huggingface_hub import HfApi

from app.config import Settings


def upload_model(pipeline, user_id: str, model_id: str) -> tuple[str, str]:
    settings = Settings()
    if not settings.HF_REPO_ID:
        raise RuntimeError("HF_REPO_ID is not configured")
    with tempfile.NamedTemporaryFile(suffix=".joblib", delete=False) as tmp:
        joblib.dump(pipeline, tmp.name)
        local_path = tmp.name
    hf_path = f"{user_id}/{model_id}/model.joblib"
    api = HfApi(token=settings.HF_WRITE_TOKEN or None)
    commit = api.upload_file(
        path_or_fileobj=local_path,
        path_in_repo=hf_path,
        repo_id=settings.HF_REPO_ID,
        repo_type="model",
    )
    revision = getattr(commit, "oid", None) or getattr(commit, "commit_oid", None) or str(uuid.uuid4())
    os.remove(local_path)
    return hf_path, revision
