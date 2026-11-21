import pandas as pd

from worker.compiler import build_pipeline, feature_schema
from worker.plan_schema import CleaningPlan
from worker.trainers import get_estimator


def test_pipeline_fits_on_fixture():
    df = pd.DataFrame({"age": [20, 30, 40, 50], "city": ["A", None, "A", "C"],
                       "target": [0, 1, 0, 1]})
    plan = CleaningPlan.model_validate({"columns": [
        {"name": "age", "action": "keep", "reason": "numeric", "impute": "median", "scale": "standard"},
        {"name": "city", "action": "keep", "reason": "categorical", "impute": "mode", "encode": "onehot"},
        {"name": "target", "action": "drop", "reason": "target"},
    ], "row_rules": {"drop_missing_target": True}})
    pipeline = build_pipeline(plan, get_estimator("random_forest", "classification"))
    pipeline.fit(df[["age", "city"]], df["target"])
    assert pipeline.predict(df[["age", "city"]]).shape == (4,)


def test_feature_schema_matches_input():
    df = pd.DataFrame({"age": [20], "city": ["A"], "target": [1]})
    plan = CleaningPlan.model_validate({"columns": [
        {"name": "age", "action": "keep", "reason": "numeric"},
        {"name": "city", "action": "keep", "reason": "categorical"},
        {"name": "target", "action": "drop", "reason": "target"},
    ], "row_rules": {}})
    assert feature_schema(plan, df) == {"age": "number", "city": "string"}
