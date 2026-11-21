from fastapi import FastAPI

from mlp_common.logging import request_id_middleware, setup_json_logging
from mlp_common.metrics import setup_metrics

from .routes.jobs import router


def create_app() -> FastAPI:
    setup_json_logging("training-api")
    app = FastAPI(title="ML Platform Training")
    request_id_middleware(app)
    setup_metrics(app)
    app.include_router(router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
