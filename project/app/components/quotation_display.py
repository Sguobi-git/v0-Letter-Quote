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
# from components.quotation_display import display_quotation_details  # We'll define our own below

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

# --- Persistent Login Utilities ---

LOGIN_FILE = os.path.join(os.path.dirname(__file__), "login_state.json")

def save_login_state(username: str) -> None:
    """Save the currently logged-in username to a file."""
    try:
        with open(LOGIN_FILE, "w") as f:
            json.dump({"username": username}, f)
    except Exception:
        pass

def load_login_state() -> Optional[str]:
    """Load the currently logged-in username from a file."""
    if not os.path.exists(LOGIN_FILE):
        return None
    try:
        with open(LOGIN_FILE, "r") as f:
            data = json.load(f)
            return data.get("username")
    except Exception:
        return None

def clear_login_state() -> None:
    """Remove the persistent login file."""
    try:
        if os.path.exists(LOGIN_FILE):
            os.remove(LOGIN_FILE)
    except Exception:
        pass

def login_signup_form():
    """Streamlit login/signup form with persistent login support."""
    st.title("Login or Sign Up")
    tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

    with tab_login:
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        remember_me = st.checkbox("Remember me", key="remember_me")
        login_btn = st.button("Login", key="login_btn")
        if login_btn:
            if authenticate_user(login_username, login_password):
                st.session_state.authenticated = True
                st.session_state.username = login_username
                if remember_me:
                    save_login_state(login_username)
                else:
                    clear_login_state()
                st.success("Logged in successfully!")
                st.experimental_rerun()
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
        # Try to load persistent login
        username = load_login_state()
        if username is not None:
            # Check if user still exists
            users = load_users()
            if username in users:
                st.session_state.authenticated = True
                st.session_state.username = username
            else:
                st.session_state.authenticated = False
                st.session_state.username = None
                clear_login_state()
        else:
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
        # Instead of calling display_quotation_details() with no argument,
        # show a list of saved quotations and allow user to select one to view details.
        if not st.session_state.quotations:
            st.info("No saved quotations yet.")
        else:
            st.markdown("### Saved Quotations")
            # List quotations with a selectbox or radio
            quote_labels = [
                f"#{i+1}: {q['letters']} ({q.get('material', 'Material')}, {q.get('color', 'Color')})"
                for i, q in enumerate(st.session_state.quotations)
            ]
            selected_idx = st.selectbox(
                "Select a quotation to view details:",
                options=list(range(len(st.session_state.quotations))),
                format_func=lambda i: quote_labels[i],
                key="quote_select_idx"
            )
            # Only call display_quotation_details if a valid index is selected
            if selected_idx is not None and 0 <= selected_idx < len(st.session_state.quotations):
                display_quotation_details(selected_idx)

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

def display_quotation_details(quote_idx: int) -> None:
    """Display detailed information for a specific quotation."""
    if 0 <= quote_idx < len(st.session_state.quotations):
        quote = st.session_state.quotations[quote_idx]
        
        # Display in an expander
        with st.expander("Quotation Details", expanded=True):            
            # Basic information
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Order Information")
                st.markdown(f"**Quotation #:** {quote_idx + 1}")
                st.markdown(f"**Letters:** {quote['letters']}")
                st.markdown(f"**Font:** {quote.get('font', 'Default')}")
                st.markdown(f"**Material:** {quote['material']}")
                st.markdown(f"**Dimensions:** {quote['dimensions']}")
                st.markdown(f"**Sets of Letters:** {quote['quantity']}")
                st.markdown(f"**Total Letters:** {quote['total_letters']}")
                st.markdown(f"**Finish:** {quote['finish']}")
                
                # Display color information
                if quote.get('multi_color', False):
                    st.markdown("### Color Information")
                    for letter, color in quote['letter_colors'].items():
                        st.markdown(f"- Letter '{letter}': <span style='color:{color['hex']}'>\u25A0</span> {color['name']}", unsafe_allow_html=True)
                else:
                    st.markdown(f"**Color:** <span style='color:{quote['color_hex']}'>\u25A0</span> {quote['color']}", unsafe_allow_html=True)
            
            with col2:
                st.markdown("### Options & Pricing")
                # Display selected options
                st.markdown("**Selected Options:**")
                for option, selected in quote['options'].items():
                    st.markdown(f"- {option}: {'Yes' if selected else 'No'}")
                
                # Cost breakdown
                st.markdown("### Cost Breakdown")
                costs = quote['costs']
                st.markdown(f"Material Cost: {format_currency(costs['material_cost'])}")
                st.markdown(f"Finish Cost: {format_currency(costs['finish_cost'])}")
                st.markdown(f"Options Cost: {format_currency(costs['options_cost'])}")
                st.markdown(f"**Subtotal:** {format_currency(costs['subtotal'])}")
                
                # Display discount if applicable
                if costs.get('discount', 0) > 0:
                    st.markdown(f"**Bulk Discount ({costs['discount_percentage']}%):** -{format_currency(costs['discount'])}")
                
                st.markdown(f"**Tax (10%):** {format_currency(costs['tax'])}")
                st.markdown(f"**Final Total:** {format_currency(costs['total'])}")
                
                # Display estimated delivery time
                if 'estimated_delivery_days' in quote:
                    delivery_days = quote['estimated_delivery_days']
                    delivery_date = datetime.now().strftime("%B %d, %Y")  # In a real app, calculate from saved date
                    st.markdown(f"**Production Time:** {delivery_days} business days")
        
        # Add export tab
        st.markdown("### Export Options")
        
        # Pre-generate the export data to avoid timing issues
        csv_data = export_to_csv(quote)
        pdf_data = export_to_pdf(quote)

        # CSV download button
        st.download_button(
            label="Download Quotation as CSV",
            data=csv_data,
            file_name="quotation.csv",
            mime="text/csv"
        )
        
        # PDF download button
        st.download_button(
            label="Download Quotation as PDF",
            data=pdf_data,
            file_name="quotation.pdf",
            mime="application/pdf"
        )

        col1, col2 = st.columns(2)
        
        with col1:
            # Direct download button with pre-generated CSV data
            st.download_button(
                label="Export as CSV",
                data=csv_data,
                file_name=f"quotation_{quote['letters'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                key=f"download_csv_{quote_idx}",
                use_container_width=True,
                help="Download quote as CSV format for spreadsheets"
            )
        
        with col2:
            # Direct download button with pre-generated PDF data
            st.download_button(
                label="Export as PDF", 
                data=pdf_data,
                file_name=f"quotation_{quote['letters'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                key=f"download_pdf_{quote_idx}",
                use_container_width=True,
                help="Download quote as PDF document"
            )

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
        clear_login_state()
        st.rerun()

if __name__ == "__main__":
    main()
