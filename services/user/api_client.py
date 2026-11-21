import os

import requests

AUTH_URL = os.getenv("AUTH_URL", "http://auth:8000")
TRAINING_URL = os.getenv("TRAINING_URL", "http://training-api:8000")
INFERENCE_URL = os.getenv("INFERENCE_URL", "http://inference:8000")


def _headers(token):
    return {"Authorization": f"Bearer {token}"} if token else {}


def register(email: str, password: str):
    response = requests.post(f"{AUTH_URL}/auth/register", json={"email": email, "password": password}, timeout=10)
    response.raise_for_status()
    return response.json()["access_token"]


def login(email: str, password: str):
    response = requests.post(f"{AUTH_URL}/auth/login", json={"email": email, "password": password}, timeout=10)
    response.raise_for_status()
    return response.json()["access_token"]


def submit_training(token, file, algo, task_type, target_col, ai_cleaning):
    response = requests.post(
        f"{TRAINING_URL}/train",
        headers=_headers(token),
        data={"algo": algo, "task_type": task_type, "target_col": target_col, "ai_cleaning": str(ai_cleaning)},
        files={"file": (file.name, file.getvalue(), "text/csv")},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def get_job(token, job_id):
    response = requests.get(f"{TRAINING_URL}/jobs/{job_id}", headers=_headers(token), timeout=10)
    response.raise_for_status()
    return response.json()


def list_jobs(token):
    response = requests.get(f"{TRAINING_URL}/jobs", headers=_headers(token), timeout=10)
    response.raise_for_status()
    return response.json()


def list_models(token):
    response = requests.get(f"{INFERENCE_URL}/models", headers=_headers(token), timeout=10)
    response.raise_for_status()
    return response.json()


def get_model(token, model_id):
    response = requests.get(f"{INFERENCE_URL}/models/{model_id}", headers=_headers(token), timeout=10)
    response.raise_for_status()
    return response.json()


def predict(token, model_id, features):
    response = requests.post(
        f"{INFERENCE_URL}/predict/{model_id}", headers=_headers(token), json=features, timeout=30
    )
    response.raise_for_status()
    return response.json()
