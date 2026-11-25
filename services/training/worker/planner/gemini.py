import json
import time

from google import genai
from google.genai import types

from .base import Planner


class PlannerError(RuntimeError):
    pass


PLAN_RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "columns": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "name": {"type": "STRING"},
                    "action": {"type": "STRING", "enum": ["keep", "drop"]},
                    "reason": {"type": "STRING"},
                    "impute": {
                        "type": "STRING",
                        "enum": ["median", "mean", "mode", "constant", "none"],
                    },
                    "encode": {
                        "type": "STRING",
                        "enum": ["onehot", "ordinal", "none"],
                    },
                    "scale": {"type": "STRING", "enum": ["none", "standard"]},
                },
                "required": ["name", "action", "reason", "impute", "encode", "scale"],
            },
        },
        "row_rules": {
            "type": "OBJECT",
            "properties": {
                "drop_missing_target": {"type": "BOOLEAN"},
            },
            "required": ["drop_missing_target"],
        },
    },
    "required": ["columns", "row_rules"],
}


def build_prompt(profile: dict, task_type: str, target_col: str) -> str:
    return (
        "Return JSON only matching: "
        '{"columns":[{"name":"column","action":"keep|drop","reason":"text",'
        '"impute":"median|mean|mode|constant|none","encode":"onehot|ordinal|none","scale":"none|standard"}],'
        '"row_rules":{"drop_missing_target":true}}. '
        f"The task type is {task_type}. Include every column in profile.columns exactly once. "
        f"Include target column {target_col!r} exactly once with action 'drop'; never keep it. "
        "Use only the aggregate profile below. "
        f"Profile: {json.dumps(profile, ensure_ascii=False)}"
    )


class GeminiPlanner(Planner):
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash", timeout: float = 10):
        self.timeout = timeout
        if not api_key:
            raise PlannerError("Gemini API key is not configured")
        self.model = model
        self.client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=int(timeout * 1000)),
        )

    def plan(self, profile: dict, task_type: str, target_col: str) -> dict:
        prompt = build_prompt(profile, task_type, target_col)
        last_error = None
        for attempt in range(2):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=PLAN_RESPONSE_SCHEMA,
                    ),
                )
                return json.loads(response.text)
            except Exception as exc:
                last_error = exc
                if attempt == 0:
                    time.sleep(0.2)
        raise PlannerError(str(last_error))
