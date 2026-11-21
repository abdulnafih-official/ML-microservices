# ML Platform

An end-to-end microservice demo for authentication, AI-assisted training, model storage,
inference, and monitoring.

## Architecture

- PostgreSQL stores auth, training queue, and model metadata
- Auth service issues JWTs and enforces model quotas
- Training API validates uploads and queues jobs
- Training worker profiles data, creates cleaning plans, trains pipelines, and uploads models
- Inference service downloads private Hugging Face artifacts and serves predictions
- Streamlit provides the user interface
- Prometheus and Grafana provide metrics

## Quick start

1. Copy `.env.example` to `.env` and set secrets and optional provider credentials.
2. Run `docker compose up --build`.
3. Open Streamlit at `http://localhost:8501`.
4. Open Grafana at `http://localhost:3000` and Prometheus at `http://localhost:9090`.

## Development

Run `make test` for unit tests or `make logs` to follow service logs.

## AI-assisted cleaning

The Gemini planner receives aggregate-only column profiles and produces a JSON cleaning
plan. Hard validation rejects malformed plans, unknown operations, duplicate columns,
unknown columns, target features, and unsafe AI output. ID-like, near-constant, and
high-cardinality rules always override the AI; rules planner is the fallback.

## Design decisions

Training jobs are claimed atomically with `FOR UPDATE SKIP LOCKED`. Quota reservation is
an atomic database update. Model artifacts are private and cached by model ID. Payload
validation rejects missing, extra, and wrongly typed fields.

## Observability

The platform exposes `/metrics` on auth, training API, training worker, and inference.
Prometheus scraping and Grafana provisioning are included.
