import pytest

from worker.planner import gemini
from worker.planner.gemini import GeminiPlanner, PlannerError


def test_gemini_planner_uses_new_sdk_and_parses_json(monkeypatch):
    class FakeModels:
        def generate_content(self, **kwargs):
            self.kwargs = kwargs
            return type("Response", (), {"text": '{"columns": []}'})()

    class FakeClient:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.models = FakeModels()

    monkeypatch.setattr(gemini.genai, "Client", FakeClient)
    planner = GeminiPlanner("test-key", "test-model", timeout=7.5)

    assert planner.client.kwargs["http_options"].timeout == 7500
    result = planner.plan({"columns": {}}, "classification", "label")
    assert result == {"columns": []}
    assert planner.client.models.kwargs["model"] == "test-model"
    assert planner.client.models.kwargs["config"].response_mime_type == "application/json"


def test_gemini_planner_requires_api_key():
    with pytest.raises(PlannerError, match="API key"):
        GeminiPlanner("")
