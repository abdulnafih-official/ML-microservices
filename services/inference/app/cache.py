import os
import threading

import joblib

from mlp_common.metrics import model_cache_hits_total, model_cache_misses_total

from .config import Settings
from .hf_loader import download_model

_locks: dict[str, threading.Lock] = {}
_locks_guard = threading.Lock()


def cache_path(model_id: str) -> str:
    settings = Settings()
    os.makedirs(settings.CACHE_DIR, exist_ok=True)
    return os.path.join(settings.CACHE_DIR, f"{model_id}.joblib")


def touch(path: str) -> None:
    if os.path.isfile(path):
        os.utime(path, None)


def get_pipeline(model_row) -> object:
    model_id = str(model_row["id"])
    with _locks_guard:
        lock = _locks.setdefault(model_id, threading.Lock())
    path = cache_path(model_id)
    with lock:
        if os.path.isfile(path):
            touch(path)
            model_cache_hits_total.inc()
            return joblib.load(path)
        model_cache_misses_total.inc()
        settings = Settings()
        downloaded = download_model(
            model_row["hf_repo"], model_row["hf_path"], model_row["hf_revision"], settings.CACHE_DIR
        )
        os.makedirs(os.path.dirname(path), exist_ok=True)
        pipeline = joblib.load(downloaded)
        joblib.dump(pipeline, path)
        touch(path)
        return pipeline
