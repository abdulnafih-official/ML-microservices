from mlp_common.config import BaseServiceSettings


class Settings(BaseServiceSettings):
    HF_REPO_ID: str = ""
    HF_READ_TOKEN: str = ""
    HF_WRITE_TOKEN: str = ""
    CACHE_DIR: str = "/tmp/model-cache"
    CACHE_TTL_MINUTES: int = 30
