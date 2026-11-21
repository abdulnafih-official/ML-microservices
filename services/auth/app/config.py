from mlp_common.config import BaseServiceSettings


class Settings(BaseServiceSettings):
    TOKEN_TTL_MINUTES: int = 60
    FREE_MODEL_LIMIT: int = 2
    RATE_LIMIT_REQUESTS: int = 10
    RATE_LIMIT_WINDOW_SECONDS: int = 60
