import pandas as pd
import streamlit as st

from api_client import list_models, predict, predict_batch
from session import get_token, require_login


def build_form_from_schema(feature_schema: dict) -> dict:
    features = {}
    for name, kind in feature_schema.items():
        if kind == "number":
            features[name] = st.number_input(name)
        else:
            features[name] = st.text_input(name)
    return features


st.title("Predict")
if require_login():
    token = get_token()
    try:
        models = list_models(token)
    except Exception as exc:
        st.error(str(exc))
        models = []
    if not models:
        st.info("No models available")
    else:
        labels = {model["name"]: model["id"] for model in models}
        selected = st.selectbox("Model", list(labels))
        model = next(model for model in models if model["id"] == labels[selected])
        mode = st.radio("Prediction mode", ["Single row", "Upload CSV for batch prediction"])
        if mode == "Single row":
            features = build_form_from_schema(model["feature_schema"])
            if st.button("Predict"):
                try:
                    result = predict(token, model["id"], features)
                    st.success(result["prediction"])
                    if "probabilities" in result:
                        st.bar_chart(result["probabilities"])
                except Exception as exc:
                    st.error(str(exc))
        else:
            uploaded = st.file_uploader("Test dataset CSV", type=["csv"])
            if uploaded:
                try:
                    dataset = pd.read_csv(uploaded)
                except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as exc:
                    st.error(f"Could not read CSV: {exc}")
                else:
                    if dataset.empty:
                        st.error("CSV must contain at least one data row")
                        st.stop()
                    feature_columns = list(model["feature_schema"])
                    missing = [name for name in feature_columns if name not in dataset.columns]
                    if missing:
                        st.error(f"CSV is missing required model features: {', '.join(missing)}")
                    else:
                        ignored = [name for name in dataset.columns if name not in feature_columns]
                        if ignored:
                            st.caption(
                                "Columns not used by this model will be ignored: "
                                + ", ".join(ignored)
                            )
                        batch = dataset.loc[:, feature_columns].copy()
                        invalid_numeric = []
                        for name, kind in model["feature_schema"].items():
                            if kind == "number":
                                converted = pd.to_numeric(batch[name], errors="coerce")
                                if (batch[name].notna() & converted.isna()).any():
                                    invalid_numeric.append(name)
                                batch[name] = converted
                            else:
                                batch[name] = batch[name].map(
                                    lambda value: value if pd.isna(value) else str(value)
                                )
                        if invalid_numeric:
                            st.error(
                                "These model features contain non-numeric values: "
                                + ", ".join(invalid_numeric)
                            )
                        else:
                            st.caption(f"{len(batch):,} rows ready for prediction")
                            st.dataframe(batch.head())
                            if st.button("Predict dataset"):
                                try:
                                    results = predict_batch(
                                        token,
                                        model["id"],
                                        batch.to_dict(orient="records"),
                                    )
                                    output = batch.copy()
                                    output["prediction"] = [row["prediction"] for row in results]
                                    if results and "probabilities" in results[0]:
                                        probability_columns = {
                                            f"probability_{label}": [
                                                row["probabilities"][label] for row in results
                                            ]
                                            for label in results[0]["probabilities"]
                                        }
                                        for name, values in probability_columns.items():
                                            output[name] = values
                                    st.dataframe(output)
                                    st.download_button(
                                        "Download predictions",
                                        output.to_csv(index=False).encode("utf-8"),
                                        file_name="predictions.csv",
                                        mime="text/csv",
                                    )
                                except Exception as exc:
                                    st.error(str(exc))
