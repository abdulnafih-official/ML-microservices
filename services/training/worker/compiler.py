import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder, StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

from .plan_schema import CleaningPlan


def build_preprocessor(plan: CleaningPlan) -> ColumnTransformer:
    transformers = []
    for column in plan.columns:
        if column.action.value != "keep":
            continue
        steps = []
        if column.impute.value != "none":
            strategy = column.impute.value
            if strategy == "constant":
                steps.append(("imputer", SimpleImputer(strategy="constant", fill_value=0)))
            else:
                steps.append(("imputer", SimpleImputer(strategy=strategy)))
        if column.encode.value == "onehot":
            steps.append(("encoder", OneHotEncoder(handle_unknown="ignore")))
        elif column.encode.value == "ordinal":
            steps.append(("encoder", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)))
        elif column.scale.value == "standard":
            steps.append(("scaler", StandardScaler()))
        if steps:
            transformers.append((column.name, Pipeline(steps), [column.name]))
    return ColumnTransformer(transformers, remainder="drop")


def build_pipeline(plan: CleaningPlan, estimator) -> Pipeline:
    return Pipeline([("preprocessor", build_preprocessor(plan)), ("estimator", estimator)])


def feature_schema(plan: CleaningPlan, df: pd.DataFrame) -> dict:
    schema = {}
    for column in plan.columns:
        if column.action.value == "keep" and column.name in df.columns:
            series = df[column.name]
            schema[column.name] = "number" if pd.api.types.is_numeric_dtype(series) else "string"
    return schema
