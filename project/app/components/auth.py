import streamlit as st
import hashlib
import os
import json
from typing import Dict, Optional, Tuple, Any

# Default admin credentials
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "password123"  # In production, this would be a hashed password

def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def load_user_credentials() -> Dict[str, str]:
    """Load user credentials from a file or use defaults."""
    try:
        if os.path.exists("data/users.json"):
            with open("data/users.json", "r") as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading user credentials: {e}")
    
    # Return default credentials if file doesn't exist or has issues
    return {DEFAULT_USERNAME: hash_password(DEFAULT_PASSWORD)}

def save_user_credentials(credentials: Dict[str, str]) -> None:
    """Save user credentials to a file."""
    try:
        os.makedirs("data", exist_ok=True)
        with open("data/users.json", "w") as f:
            json.dump(credentials, f)
    except Exception as e:
        st.error(f"Error saving user credentials: {e}")

def check_authentication() -> bool:
    """Check if user is authenticated."""
    return st.session_state.get("authenticated", False)

def login_form() -> None:
    """Display login form and handle authentication."""
    st.header("Login to 3D Letter Quotation Calculator")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        login_button = st.form_submit_button("Login")
        
        if login_button:
            credentials = load_user_credentials()
            
            if username in credentials and credentials[username] == hash_password(password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    # Guest access option
    st.markdown("---")
    if st.button("Continue as Guest"):
        st.session_state.authenticated = True
        st.session_state.username = "guest"
        st.rerun()

def change_password_form() -> None:
    """Form for changing the user password."""
    st.subheader("Change Password")
    
    with st.form("change_password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        submit_button = st.form_submit_button("Change Password")
        
        if submit_button:
            if new_password != confirm_password:
                st.error("New passwords do not match")
                return
            
            credentials = load_user_credentials()
            username = st.session_state.username
            
            if username in credentials and credentials[username] == hash_password(current_password):
                credentials[username] = hash_password(new_password)
                save_user_credentials(credentials)
                st.success("Password changed successfully")
                st.session_state.show_password_change = False
            else:
                st.error("Current password is incorrect")