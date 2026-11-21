import json
import time

import google.generativeai as genai

from .base import Planner


class PlannerError(RuntimeError):
    pass


def build_prompt(profile: dict, task_type: str, target_col: str) -> str:
    return (
        "Return JSON only matching: "
        '{"columns":[{"name":"column","action":"keep|drop","reason":"text",'
        '"impute":"median|mean|mode|constant|none","encode":"onehot|ordinal|none","scale":"none|standard"}],'
        '"row_rules":{"drop_missing_target":true}}. '
        f"The task type is {task_type}. Never include target column {target_col!r} as a feature "
        "and describe every column exactly once. Use only the aggregate profile below. "
        f"Profile: {json.dumps(profile, ensure_ascii=False)}"
    )


class GeminiPlanner(Planner):
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash", timeout: float = 10):
        self.timeout = timeout
        if not api_key:
            raise PlannerError("Gemini API key is not configured")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

    def plan(self, profile: dict, task_type: str, target_col: str) -> dict:
        prompt = build_prompt(profile, task_type, target_col)
        last_error = None
        for attempt in range(2):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config={"response_mime_type": "application/json"},
                    request_options={"timeout": self.timeout},
                )
                return json.loads(response.text)
            except Exception as exc:
                last_error = exc
                if attempt == 0:
                    time.sleep(0.2)
        raise PlannerError(str(last_error))
