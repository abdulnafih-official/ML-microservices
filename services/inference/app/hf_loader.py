import os

from huggingface_hub import HfApi, hf_hub_download

from .config import Settings


def download_model(hf_repo: str, hf_path: str, hf_revision: str, dest_dir: str) -> str:
    os.makedirs(dest_dir, exist_ok=True)
    settings_token = Settings().HF_READ_TOKEN or None
    return hf_hub_download(
        repo_id=hf_repo,
        filename=hf_path,
        revision=hf_revision,
        token=settings_token,
        cache_dir=dest_dir,
    )


def delete_model_file(hf_repo: str, hf_path: str) -> None:
    settings = Settings()
    if not settings.HF_WRITE_TOKEN or "<FILLME>" in settings.HF_WRITE_TOKEN:
        raise RuntimeError("HF_WRITE_TOKEN must be configured to delete models")
    HfApi(token=settings.HF_WRITE_TOKEN).delete_file(
        path_in_repo=hf_path,
        repo_id=hf_repo,
        repo_type="model",
        commit_message=f"Delete trained model artifact: {hf_path}",
    )
