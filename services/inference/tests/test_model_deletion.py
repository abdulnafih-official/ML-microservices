import pytest

from app import hf_loader
from app.hf_loader import delete_model_file


def test_delete_model_file_uses_write_token(monkeypatch):
    calls = {}

    class FakeHfApi:
        def __init__(self, token):
            calls["token"] = token

        def delete_file(self, **kwargs):
            calls["kwargs"] = kwargs

    monkeypatch.setenv("HF_WRITE_TOKEN", "test-token")
    monkeypatch.setattr(hf_loader, "HfApi", FakeHfApi)

    delete_model_file("account/private-models", "user/model/model.joblib")

    assert calls["token"] == "test-token"
    assert calls["kwargs"]["repo_id"] == "account/private-models"
    assert calls["kwargs"]["path_in_repo"] == "user/model/model.joblib"


def test_delete_model_file_requires_write_token(monkeypatch):
    monkeypatch.setenv("HF_WRITE_TOKEN", "")

    with pytest.raises(RuntimeError, match="HF_WRITE_TOKEN"):
        delete_model_file("account/private-models", "user/model/model.joblib")
