from sklearn.metrics import accuracy_score, f1_score, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
import numpy as np


def split_data(df, target_col: str, task_type: str):
    X = df.drop(columns=[target_col])
    y = df[target_col]
    stratify = y if task_type == "classification" else None
    return train_test_split(X, y, test_size=0.2, random_state=42, stratify=stratify)


def compute_metrics(pipeline, X_test, y_test, task_type: str) -> dict:
    prediction = pipeline.predict(X_test)
    if task_type == "classification":
        return {
            "accuracy": float(accuracy_score(y_test, prediction)),
            "f1": float(f1_score(y_test, prediction, average="weighted", zero_division=0)),
        }
    return {
        "rmse": float(np.sqrt(mean_squared_error(y_test, prediction))),
        "r2": float(r2_score(y_test, prediction)),
    }
