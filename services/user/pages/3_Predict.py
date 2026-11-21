import streamlit as st

from api_client import list_models, predict
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
        features = build_form_from_schema(model["feature_schema"])
        if st.button("Predict"):
            try:
                result = predict(token, model["id"], features)
                st.success(result["prediction"])
                if "probabilities" in result:
                    st.bar_chart(result["probabilities"])
            except Exception as exc:
                st.error(str(exc))
