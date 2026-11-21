import streamlit as st
import requests

from api_client import login, register
from session import set_token

st.set_page_config(page_title="ML Platform", page_icon="ML")

st.title("ML Platform")
tabs = st.tabs(["Login", "Register"])

with tabs[0]:
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        try:
            set_token(login(email, password))
            st.success("Logged in")
        except requests.HTTPError as exc:
            st.error(exc.response.text if exc.response is not None else str(exc))

with tabs[1]:
    email = st.text_input("Email", key="register_email")
    password = st.text_input("Password", type="password", key="register_password")
    if st.button("Register"):
        try:
            set_token(register(email, password))
            st.success("Account created")
        except requests.HTTPError as exc:
            st.error(exc.response.text if exc.response is not None else str(exc))
