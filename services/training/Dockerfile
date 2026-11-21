FROM python:3.11-slim
WORKDIR /app
COPY shared/mlp_common /tmp/mlp_common
RUN pip install --no-cache-dir /tmp/mlp_common
COPY services/training/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY services/training/app /app/app
COPY services/training/worker /app/worker
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
