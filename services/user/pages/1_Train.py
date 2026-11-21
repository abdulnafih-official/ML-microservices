import time

import pandas as pd
import requests
import streamlit as st

from api_client import get_job, submit_training
from session import get_token, require_login

st.title("Train a model")
if require_login():
    token = get_token()
    uploaded = st.file_uploader("Training CSV", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded)
        st.dataframe(df.head())
        target = st.selectbox("Target column", df.columns)
        task_type = st.selectbox("Task type", ["classification", "regression"])
        algo = st.selectbox("Algorithm", ["random_forest", "xgboost"])
        ai_cleaning = st.toggle("AI-assisted cleaning", value=True)
        if st.button("Start training"):
            uploaded.seek(0)
            try:
                job = submit_training(token, uploaded, algo, task_type, target, ai_cleaning)
                st.session_state["training_job"] = job["id"]
                st.success("Training job queued")
            except requests.HTTPError as exc:
                status = exc.response.status_code if exc.response is not None else None
                if status == 403:
                    st.error("Model quota exceeded")
                else:
                    st.error(exc.response.text if exc.response is not None else str(exc))

    job_id = st.session_state.get("training_job")
    if job_id:
        st.subheader("Job status")
        placeholder = st.empty()
        for _ in range(60):
            try:
                job = get_job(token, job_id)
            except requests.HTTPError as exc:
                placeholder.error(exc.response.text if exc.response is not None else str(exc))
                break
            placeholder.write(f"Status: **{job['status']}**")
            if job["status"] in ("succeeded", "failed"):
                if job["status"] == "failed":
                    placeholder.error(job.get("error") or "Training failed")
                else:
                    placeholder.success("Training succeeded")
                    if job.get("model_id"):
                        st.info(f"Model ID: {job['model_id']}")
                break
            time.sleep(2)
