from mlp_common.config import BaseServiceSettings


class Settings(BaseServiceSettings):
    AUTH_URL: str = "http://auth:8000"
    MAX_UPLOAD_MB: int = 10
    MAX_ROWS: int = 100000
    UPLOAD_DIR: str = "/tmp/uploads"
    JOB_TIMEOUT_MINUTES: int = 30
    MAX_JOB_ATTEMPTS: int = 3
    HF_REPO_ID: str = ""
    HF_WRITE_TOKEN: str = ""
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
