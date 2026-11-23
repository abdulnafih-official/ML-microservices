from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseServiceSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    JWT_SECRET: str = ""
    DATABASE_URL: str = "postgresql+psycopg2://mlplatform:mlplatform@postgres:5432/mlplatform"
    INTERNAL_API_KEY: str = ""
