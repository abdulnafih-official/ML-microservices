import os

from huggingface_hub import hf_hub_download


def download_model(hf_repo: str, hf_path: str, hf_revision: str, dest_dir: str) -> str:
    os.makedirs(dest_dir, exist_ok=True)
    settings_token = os.environ.get("HF_READ_TOKEN") or None
    return hf_hub_download(
        repo_id=hf_repo,
        filename=hf_path,
        revision=hf_revision,
        token=settings_token,
        cache_dir=dest_dir,
    )
