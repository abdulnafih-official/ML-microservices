import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from mlp_common.logging import request_id_middleware, setup_json_logging
from mlp_common.metrics import setup_metrics

from .routes.models import router as models_router
from .routes.predict import router as predict_router
from .sweeper import run_sweeper


def create_app() -> FastAPI:
    setup_json_logging("inference")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        task = asyncio.create_task(run_sweeper(60))
        yield
        task.cancel()

    app = FastAPI(title="ML Platform Inference", lifespan=lifespan)
    request_id_middleware(app)
    setup_metrics(app)
    app.include_router(models_router)
    app.include_router(predict_router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
