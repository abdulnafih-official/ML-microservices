from prometheus_client import Counter, Gauge, Histogram
from prometheus_fastapi_instrumentator import Instrumentator

quota_rejections_total = Counter("quota_rejections_total", "Quota reservations rejected")
training_jobs_total = Counter("training_jobs_total", "Training jobs finished", ["status"])
training_duration_seconds = Histogram("training_duration_seconds", "Training job duration")
training_queue_length = Gauge("training_queue_length", "Queued training jobs")
model_cache_hits_total = Counter("model_cache_hits_total", "Model cache hits")
model_cache_misses_total = Counter("model_cache_misses_total", "Model cache misses")
llm_plan_total = Counter("llm_plan_total", "LLM planner outcomes", ["outcome"])


def setup_metrics(app) -> None:
    Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
