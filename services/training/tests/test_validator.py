import pytest

from worker.plan_schema import CleaningPlan
from worker.validator import PlanInvalid, apply_hard_rules, is_id_like, validate_plan


def test_unknown_operation_rejected():
    with pytest.raises(PlanInvalid):
        validate_plan({"columns": [{"name": "x", "action": "unknown", "reason": "x"}],
                       "row_rules": {}}, ["x"], "y")


def test_missing_column_rejected():
    with pytest.raises(PlanInvalid):
        validate_plan({"columns": [], "row_rules": {}}, ["x"], "y")


def test_target_dropped_rejected():
    with pytest.raises(PlanInvalid):
        validate_plan({"columns": [
            {"name": "x", "action": "keep", "reason": "x"},
            {"name": "y", "action": "keep", "reason": "target"},
        ], "row_rules": {}}, ["x", "y"], "y")


def test_id_like_force_dropped():
    plan = CleaningPlan.model_validate({"columns": [
        {"name": "customer_id", "action": "keep", "reason": "feature"},
    ], "row_rules": {}})
    profile = {"columns": {"customer_id": {"n_unique": 100, "unique_ratio": 1}}}
    assert apply_hard_rules(plan, profile).columns[0].action.value == "drop"
    assert is_id_like("customer_id", {"unique_ratio": 0.1})
