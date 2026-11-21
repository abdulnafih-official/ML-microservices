import math

import pandas as pd


def profile_column(series: pd.Series) -> dict:
    s = series.dropna()
    unique = int(series.nunique(dropna=True))
    profile = {
        "dtype": str(series.dtype),
        "missing_pct": float(series.isna().mean()),
        "n_unique": unique,
        "unique_ratio": float(unique / max(len(series), 1)),
    }
    if pd.api.types.is_numeric_dtype(series):
        profile.update({
            "numeric": True,
            "min": _safe(s.min()),
            "max": _safe(s.max()),
            "mean": _safe(s.mean()),
            "std": _safe(s.std()),
            "skew": _safe(s.skew()),
        })
    else:
        profile["numeric"] = False
        if len(s):
            profile["top_categories"] = {
                str(k): int(v) for k, v in s.astype(str).value_counts().head(20).items()
            }
    return profile


def _safe(value):
    if value is None or (isinstance(value, float) and not math.isfinite(value)):
        return None
    try:
        return value.item()
    except AttributeError:
        return value


def profile_dataframe(df: pd.DataFrame, target_col: str, task_type: str) -> dict:
    return {
        "rows": len(df),
        "columns": {name: profile_column(df[name]) for name in df.columns},
        "target": target_col,
        "task_type": task_type,
        "target_distribution": (
            {str(k): int(v) for k, v in df[target_col].value_counts(dropna=False).head(100).items()}
            if target_col in df.columns else {}
        ),
    }
