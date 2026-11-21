from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from xgboost import XGBClassifier, XGBRegressor


def get_estimator(algo: str, task_type: str):
    if algo == "random_forest":
        return (
            RandomForestClassifier(random_state=42, n_jobs=-1)
            if task_type == "classification"
            else RandomForestRegressor(random_state=42, n_jobs=-1)
        )
    if task_type == "classification":
        return XGBClassifier(random_state=42, n_estimators=200, n_jobs=-1)
    return XGBRegressor(random_state=42, n_estimators=200, n_jobs=-1)
