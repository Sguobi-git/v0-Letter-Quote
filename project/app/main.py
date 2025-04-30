import streamlit as st
import pandas as pd
import os
import json
import base64
import hashlib
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timedelta

# Import components
from components.letter_preview import render_3d_preview
from components.quotation_form import render_quotation_form
from components.quotation_display import display_quotation_details

# Import utilities
from utils.calculations import calculate_costs, calculate_delivery_time, calculate_bulk_discount
from utils.validation import validate_inputs, sanitize_text_input
from utils.formatting import format_currency
from utils.export import export_to_csv, export_to_pdf

# --- User Authentication Utilities ---

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")

def hash_password(password: str) -> str:
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users() -> Dict[str, Dict[str, str]]:
    """Load users from the users.json file."""
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        try:
            return json.load(f)
        except Exception:
            return {}

def save_users(users: Dict[str, Dict[str, str]]) -> None:
    """Save users to the users.json file."""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def register_user(username: str, password: str) -> bool:
    """Register a new user. Returns True if successful, False if user exists."""
    users = load_users()
    if username in users:
        return False
    users[username] = {
        "password": hash_password(password)
    }
    save_users(users)
    return True

def authenticate_user(username: str, password: str) -> bool:
    """Authenticate user credentials."""
    users = load_users()
    if username in users and users[username]["password"] == hash_password(password):
        return True
    return False

def change_user_password(username: str, old_password: str, new_password: str) -> bool:
    """Change the password for a user. Returns True if successful."""
    users = load_users()
    if username in users and users[username]["password"] == hash_password(old_password):
        users[username]["password"] = hash_password(new_password)
        save_users(users)
        return True
    return False

def login_signup_form():
    """Streamlit login/signup form."""
    st.title("Login or Sign Up")
    tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

    with tab_login:
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        login_btn = st.button("Login", key="login_btn")
        if login_btn:
            if authenticate_user(login_username, login_password):
                st.session_state.authenticated = True
                st.session_state.username = login_username
                st.success("Logged in successfully!")
                st.experimental_rerun()
                # from streamlit.runtime.scriptrunner import rerun
                # rerun()
            else:
                st.error("Invalid username or password.")

    with tab_signup:
        signup_username = st.text_input("Choose a Username", key="signup_username")
        signup_password = st.text_input("Choose a Password", type="password", key="signup_password")
        signup_password2 = st.text_input("Confirm Password", type="password", key="signup_password2")
        signup_btn = st.button("Sign Up", key="signup_btn")
        if signup_btn:
            if not signup_username or not signup_password:
                st.warning("Please fill in all fields.")
            elif signup_password != signup_password2:
                st.warning("Passwords do not match.")
            elif len(signup_password) < 4:
                st.warning("Password must be at least 4 characters.")
            elif register_user(signup_username, signup_password):
                st.success("Account created! You can now log in.")
            else:
                st.error("Username already exists.")

# Page configuration
st.set_page_config(
    page_title="3D Letter Quotation Calculator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css() -> None:
    """Load custom CSS styles."""
    try:
        with open(r'project/app/static/css/styles.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Custom CSS file not found. Using default styles.")

# Initialize session state variables
def init_session_state() -> None:
    """Initialize all session state variables."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if 'username' not in st.session_state:
        st.session_state.username = None

    if 'quotations' not in st.session_state:
        st.session_state.quotations = []

    if 'current_quote' not in st.session_state:
        st.session_state.current_quote = None

    if 'letter_properties' not in st.session_state:
        st.session_state.letter_properties = {
            "letters": "ABC",
            "height": 12.0,
            "width": 8.0,
            "depth": 2.0,
            "material": "Wood",
            "finish": "Standard",
            "color": "Blue",
            "quantity": 1,
            "led_lighting": False,
            "mounting_hardware": False,
            "installation": False,
            "font": "default",
            "letter_colors": {}  # For multi-color support
        }

    if 'last_calculation_props' not in st.session_state:
        st.session_state.last_calculation_props = {}

def main() -> None:
    """Main application function."""
    # Load CSS and initialize session state
    load_css()
    init_session_state()

    # Handle authentication
    if not st.session_state.authenticated:
        login_signup_form()
        return

    # Application header
    with st.container():
        col1, col2 = st.columns([1, 5])
        with col1:
            st.image(r"project/app/static/images/logo.jpg", width=200)
        with col2:
            st.title("3D Letter Quotation Calculator")
            st.caption("Design custom 3D letters with real-time preview and instant pricing")

    st.markdown("---")

    # Main content with tabs
    tab1, tab2, tab3 = st.tabs(["Create New Quote", "Saved Quotes", "Settings"])

    with tab1:
        render_3d_preview()
        render_quotation_form()

    with tab2:
        # Display saved quotations
        display_saved_quotations()

    with tab3:
        # Settings tab
        render_settings()

def display_current_quotation() -> None:
    """Display the current quotation summary."""
    with st.container():
        st.subheader("Quotation Summary")
        quote = st.session_state.current_quote

        # Show spinner for loading simulation
        with st.spinner("Finalizing quotation..."):
            # Display quote details
            st.markdown(f"""
            ### Order Details
            **Letters:** {quote['letters']}  
            **Font:** {quote['font']}  
            **Material:** {quote['material']}  
            **Dimensions (per letter):** {quote['dimensions']}  
            **Number of Sets:** {quote['quantity']}  
            **Total Letters:** {quote['total_letters']}  
            **Finish:** {quote['finish']}
            """)

            # Display color information
            if quote.get('multi_color', False):
                st.markdown("### Colors")
                for i, (letter, color) in enumerate(quote['letter_colors'].items()):
                    st.markdown(f"- Letter '{letter}': <span style='color:{color['hex']}'>\u25A0</span> {color['name']}", unsafe_allow_html=True)
            else:
                st.markdown(f"**Color:** <span style='color:{quote['color_hex']}'>\u25A0</span> {quote['color']}", unsafe_allow_html=True)

            # Display selected options
            st.markdown("### Selected Options")
            for option, selected in quote['options'].items():
                st.markdown(f"- {option}: {'Yes' if selected else 'No'}")

            # Display cost breakdown
            st.markdown("### Cost Breakdown")
            costs = quote['costs']
            st.markdown(f"""
            Material Cost ({quote['volume_per_letter']:.1f} cubic inches/letter): {format_currency(costs['material_cost'])}  
            Finish Cost: {format_currency(costs['finish_cost'])}  
            Options Cost: {format_currency(costs['options_cost'])}  
            **Subtotal:** {format_currency(costs['subtotal'])}
            """)

            # Display discount if applicable
            if costs.get('discount', 0) > 0:
                st.markdown(f"**Bulk Discount ({costs['discount_percentage']}%):** -{format_currency(costs['discount'])}")

            # Display final costs
            st.markdown(f"""
            **Tax (10%):** {format_currency(costs['tax'])}  
            **Final Total:** {format_currency(costs['total'])}
            """)

            # Display estimated delivery time
            delivery_days = quote.get('estimated_delivery_days', 7)
            delivery_date = datetime.now() + timedelta(days=delivery_days)
            st.markdown(f"""
            ### Estimated Delivery
            **Production Time:** {delivery_days} business days  
            **Estimated Completion:** {delivery_date.strftime('%B %d, %Y')}
            """)

        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save Quotation", key="save_quote_btn", use_container_width=True):
                st.session_state.quotations.append(quote)
                st.success("Quotation saved successfully!")

        with col2:
            export_options = st.selectbox("Export Format", ["CSV", "PDF"], key="export_format")

            # --- PDF Download Fix ---
            # We need to use st.download_button directly, not inside a button callback.
            # So, we show the download_button only after the user clicks "Export".
            # We'll use session_state to store the export data and show the download button.

            if 'show_download' not in st.session_state:
                st.session_state.show_download = False
            if 'export_data' not in st.session_state:
                st.session_state.export_data = None
            if 'export_mime' not in st.session_state:
                st.session_state.export_mime = None
            if 'export_ext' not in st.session_state:
                st.session_state.export_ext = None

            if st.button("Export", key="export_btn", use_container_width=True):
                with st.spinner("Preparing export..."):
                    if export_options == "CSV":
                        export_data = export_to_csv(quote)
                        mime = "text/csv"
                        ext = "csv"
                    else:  # PDF
                        export_data = export_to_pdf(quote)
                        # If export_to_pdf returns a file path, read as bytes
                        if isinstance(export_data, str):
                            with open(export_data, "rb") as f:
                                export_data = f.read()
                        mime = "application/pdf"
                        ext = "pdf"
                    st.session_state.export_data = export_data
                    st.session_state.export_mime = mime
                    st.session_state.export_ext = ext
                    st.session_state.show_download = True

            if st.session_state.get("show_download", False) and st.session_state.get("export_data", None) is not None:
                file_name = f"quotation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{st.session_state.export_ext}"
                st.download_button(
                    label=f"Download {st.session_state.export_ext.upper()}",
                    data=st.session_state.export_data,
                    file_name=file_name,
                    mime=st.session_state.export_mime,
                    key=f"download_{st.session_state.export_ext}_{file_name}"
                )
                # Reset after download button is shown
                st.session_state.show_download = False

def render_settings() -> None:
    """Render the settings tab."""
    st.markdown("### Account Settings")

    # Initialize session state for password change UI
    if "show_password_change" not in st.session_state:
        st.session_state.show_password_change = False

    # Change password option
    if st.button("Change Password"):
        st.session_state.show_password_change = True

    if st.session_state.get("show_password_change", False):
        with st.form("change_password_form", clear_on_submit=True):
            st.write("Change your password")
            old_password = st.text_input("Current Password", type="password", key="old_password")
            new_password = st.text_input("New Password", type="password", key="new_password")
            new_password2 = st.text_input("Confirm New Password", type="password", key="new_password2")
            submitted = st.form_submit_button("Update Password")
            if submitted:
                if not old_password or not new_password or not new_password2:
                    st.warning("Please fill in all fields.")
                elif new_password != new_password2:
                    st.warning("New passwords do not match.")
                elif len(new_password) < 4:
                    st.warning("New password must be at least 4 characters.")
                elif not st.session_state.username:
                    st.error("No user logged in.")
                elif not change_user_password(st.session_state.username, old_password, new_password):
                    st.error("Current password is incorrect.")
                else:
                    st.success("Password updated successfully.")
                    st.session_state.show_password_change = False

        # Option to cancel password change
        if st.button("Cancel", key="cancel_password_change"):
            st.session_state.show_password_change = False

    # Log out button
    if st.button("Log Out"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()

if __name__ == "__main__":
    main()
