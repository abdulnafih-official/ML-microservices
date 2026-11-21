import re
from pydantic import ValidationError

from .plan_schema import Action, CleaningPlan, Encode


class PlanInvalid(ValueError):
    pass


def is_id_like(name: str | dict, column_profile: dict | None = None) -> bool:
    if isinstance(name, dict):
        column_profile = name
        name = str(name.get("name", ""))
    else:
        column_profile = column_profile or {}
    return bool(re.search(r"(^id$|_id$|^.*_identifier$)", name, re.I)
        or column_profile.get("unique_ratio", 0) >= 0.98)


def validate_plan(plan_raw: dict, df_columns: list[str], target_col: str) -> CleaningPlan:
    try:
        plan = CleaningPlan.model_validate(plan_raw)
    except (ValidationError, TypeError, AttributeError) as exc:
        raise PlanInvalid("Malformed cleaning plan") from exc
    names = [column.name for column in plan.columns]
    if len(names) != len(set(names)):
        raise PlanInvalid("A column appears more than once")
    if set(names) != set(df_columns):
        raise PlanInvalid("Cleaning plan must describe every dataset column exactly once")
    if target_col not in df_columns:
        raise PlanInvalid("Unknown target column")
    target = next((column for column in plan.columns if column.name == target_col), None)
    if target is not None and target.action.value == "keep":
        raise PlanInvalid("Target column cannot be a feature")
    return plan


def apply_hard_rules(plan: CleaningPlan, profile: dict) -> CleaningPlan:
    updated = []
    for column in plan.columns:
        col_profile = profile["columns"].get(column.name, {})
        if is_id_like(column.name, col_profile) or col_profile.get("n_unique", 1) <= 1:
            column = column.model_copy(update={
                "action": Action.drop,
                "reason": "Hard rule: ID-like or near-constant column",
            })
        elif column.encode.value == "onehot" and col_profile.get("n_unique", 0) > 20:
            column = column.model_copy(update={
                "encode": Encode.ordinal,
                "reason": "Hard rule: one-hot cardinality capped",
            })
        updated.append(column)
    return plan.model_copy(update={"columns": updated})
