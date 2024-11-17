# auth.py
import streamlit as st

class Authenticator:
    def __init__(self, allowed_users, token_key, secret_path, redirect_uri):
        self.allowed_users = allowed_users
        self.token_key = token_key
        self.secret_path = secret_path
        self.redirect_uri = redirect_uri

    def check_auth(self):
        if "connected" not in st.session_state:
            st.session_state["connected"] = False
            st.session_state["user_info"] = {}

    def login(self):
        # Simple mock login implementation
        user_email = st.text_input("Enter your email:")
        if st.button("Log In"):
            if user_email in self.allowed_users:
                st.session_state["connected"] = True
                st.session_state["user_info"] = {"email": user_email}
                st.success("Login successful!")
            else:
                st.error("Unauthorized user!")

    def logout(self):
        st.session_state["connected"] = False
        st.session_state["user_info"] = {}
        st.success("Logged out successfully!")
