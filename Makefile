.PHONY: up down test logs
up:
	docker compose up --build
down:
	docker compose down
test:
	PYTHONPATH=services/auth:shared/mlp_common pytest -q services/auth/tests
	PYTHONPATH=services/training:shared/mlp_common pytest -q services/training/tests
	PYTHONPATH=services/inference:shared/mlp_common pytest -q services/inference/tests
logs:
	docker compose logs -f
