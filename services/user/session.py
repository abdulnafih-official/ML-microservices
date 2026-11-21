import streamlit as st


def set_token(token: str) -> None:
    st.session_state["token"] = token


def get_token():
    return st.session_state.get("token")


def require_login() -> bool:
    if not get_token():
        st.switch_page("app.py")
        return False
    render_logout()
    return True


def render_logout() -> None:
    if get_token() and st.sidebar.button("Log out", key="logout"):
        logout()
        st.switch_page("app.py")


def logout() -> None:
    st.session_state.pop("token", None)
