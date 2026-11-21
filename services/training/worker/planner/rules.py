from .base import Planner


class RulesPlanner(Planner):
    def plan(self, profile: dict, task_type: str, target_col: str) -> dict:
        columns = []
        for name, col in profile["columns"].items():
            if name == target_col:
                columns.append({"name": name, "action": "drop", "reason": "Target is never a feature",
                                "impute": "none", "encode": "none", "scale": "none"})
                continue
            if col["n_unique"] <= 1:
                columns.append({"name": name, "action": "drop", "reason": "Near-constant column",
                                "impute": "none", "encode": "none", "scale": "none"})
            elif col["numeric"]:
                columns.append({"name": name, "action": "keep", "reason": "Numeric feature",
                                "impute": "median", "encode": "none", "scale": "standard"})
            elif col["n_unique"] <= 20:
                columns.append({"name": name, "action": "keep", "reason": "Low-cardinality categorical",
                                "impute": "mode", "encode": "onehot", "scale": "none"})
            else:
                columns.append({"name": name, "action": "drop", "reason": "High-cardinality categorical",
                                "impute": "none", "encode": "none", "scale": "none"})
        return {"columns": columns, "row_rules": {"drop_missing_target": True}}
