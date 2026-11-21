import streamlit as st

from api_client import list_models
from session import get_token, require_login

st.title("My Models")
if require_login():
    token = get_token()
    try:
        models = list_models(token)
    except Exception as exc:
        st.error(str(exc))
        models = []
    if not models:
        st.info("No models trained yet")
    for model in models:
        with st.expander(f"{model['name']} - {model['algo']}"):
            st.write("Status:", model["status"])
            st.write("Metrics:", model["metrics"])
            st.write("Plan source:", model["plan_source"])
            st.write("Fallback used:", model["fallback_used"])
            st.write("Feature schema:", model["feature_schema"])
            cleaning = model["cleaning_plan"]
            st.write("Cleaning plan:")
            for column in cleaning.get("columns", []):
                st.markdown(
                    f"- **{column['name']}**: {column['action']} - {column['reason']}"
                )
