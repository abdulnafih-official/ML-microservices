import json

import pytest

from worker.planner import gemini
from worker.planner.gemini import GeminiPlanner, PlannerError


def test_gemini_planner_uses_new_sdk_and_parses_json(monkeypatch):
    plan = {
        "columns": [{
            "name": "feature",
            "action": "keep",
            "reason": "Useful feature",
            "impute": "median",
            "encode": "none",
            "scale": "standard",
        }],
        "row_rules": {"drop_missing_target": True},
    }

    class FakeModels:
        def generate_content(self, **kwargs):
            self.kwargs = kwargs
            return type("Response", (), {"text": json.dumps(plan)})()

    class FakeClient:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.models = FakeModels()

    monkeypatch.setattr(gemini.genai, "Client", FakeClient)
    planner = GeminiPlanner("test-key", "test-model", timeout=7.5)

    assert planner.client.kwargs["http_options"].timeout == 7500
    profile = {"columns": {"feature": {}, "label": {}}}
    result = planner.plan(profile, "classification", "label")
    assert result == plan
    assert planner.client.models.kwargs["model"] == "test-model"
    config = planner.client.models.kwargs["config"]
    assert config.response_mime_type == "application/json"
    assert config.response_schema == gemini.PLAN_RESPONSE_SCHEMA
    assert "Include target column 'label' exactly once with action 'drop'" in planner.client.models.kwargs["contents"]


def test_gemini_planner_requires_api_key():
    with pytest.raises(PlannerError, match="API key"):
        GeminiPlanner("")
