import streamlit as st
import os

def is_logged_in():
    if st.session_state.user_authenticated:
        return True
    return general_login()


def general_login():
    with st.expander("🔐 Login"):
        password = st.text_input("Enter password", type="password")
        if password == os.environ.get("USER_PASSWORD"):
            st.session_state.user_authenticated = True
            st.rerun()
        elif password:
            st.error("Incorrect password")
    return False
    