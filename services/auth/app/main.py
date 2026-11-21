from fastapi import FastAPI

from mlp_common.logging import request_id_middleware, setup_json_logging
from mlp_common.metrics import setup_metrics

from .config import Settings
from .models import Base
from .db import engine
from .rate_limit import configure_limiter
from .routes.auth import router as auth_router
from .routes.internal import router as internal_router


def create_app() -> FastAPI:
    settings = Settings()
    setup_json_logging("auth")
    configure_limiter(settings.RATE_LIMIT_REQUESTS, settings.RATE_LIMIT_WINDOW_SECONDS)
    app = FastAPI(title="ML Platform Auth")
    request_id_middleware(app)
    setup_metrics(app)
    app.include_router(auth_router)
    app.include_router(internal_router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
