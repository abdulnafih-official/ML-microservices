import streamlit as st


def set_token(token: str) -> None:
    st.session_state["token"] = token


def get_token():
    return st.session_state.get("token")


def require_login() -> bool:
    if not get_token():
        st.switch_page("app.py")
        return False
    return True


def logout() -> None:
    st.session_state.pop("token", None)
