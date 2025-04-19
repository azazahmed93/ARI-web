import streamlit as st
import os

def is_admin():
    if st.session_state.admin_authenticated:
        return True
    return admin_login()


def admin_login():
    with st.expander("🔐 Admin Login"):
        password = st.text_input("Enter admin password", type="password")
        if password == os.environ.get("ADMIN_PASSWORD"):
            st.session_state.admin_authenticated = True
            st.rerun()
        elif password:
            st.error("Incorrect password")
    return False
    