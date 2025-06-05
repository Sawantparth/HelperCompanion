import streamlit as st
import json
import os
import hashlib
from datetime import datetime
import uuid
from utils.firebase_manager import firebase_manager

def render_simple_auth():
    """Render simple authentication interface."""
    # Try to initialize Firebase
    if 'firebase_initialized' not in st.session_state:
        st.session_state.firebase_initialized = firebase_manager.initialize()
        if st.session_state.firebase_initialized:
            st.success("✅ Connected to Firebase")
        else:
            st.warning("⚠️ Using local authentication (Firebase not configured)")

    st.title("🔐 Study Companion Login")
    st.markdown("Please log in to access your personalized study companion.")

    # Create tabs for login and registration
    login_tab, register_tab = st.tabs(["🔑 Login", "📝 Register"])

    with login_tab:
        authenticated = render_login_form()
        if authenticated:
            return True

    with register_tab:
        render_registration_form()

    return False

def render_login_form():
    """Render login form."""
    st.subheader("Login to Your Account")

    with st.form("login_form"):
        email = st.text_input(
            "Email Address",
            placeholder="Enter your email"
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )

        login_button = st.form_submit_button("🔑 Login", type="primary")

        if login_button:
            if email and password:
                if authenticate_user(email, password):
                    st.success("✅ Login successful!")
                    st.rerun()
                    return True
                else:
                    st.error("❌ Invalid email or password.")
            else:
                st.error("❌ Please enter both email and password.")

    return False

def render_registration_form():
    """Render registration form."""
    st.subheader("Create New Account")

    with st.form("register_form"):
        email = st.text_input(
            "Email Address",
            placeholder="Enter your email"
        )
        full_name = st.text_input(
            "Full Name",
            placeholder="Enter your full name"
        )

        # Role selection
        user_role = st.selectbox(
            "Select Your Role:",
            ["Student", "Teacher/Tutor"],
            help="Choose your role to access appropriate features"
        )

        # Additional fields for teachers
        if user_role == "Teacher/Tutor":
            subjects = st.multiselect(
                "Teaching Subjects:",
                ["Mathematics", "Physics", "Chemistry", "Biology", "Computer Science", 
                 "English", "History", "Geography", "Economics", "Other"],
                help="Select subjects you teach"
            )

            institution = st.text_input(
                "Institution/School Name (Optional):",
                placeholder="Enter your institution name"
            )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Create a password"
        )
        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Confirm your password"
        )

        register_button = st.form_submit_button("📝 Create Account", type="primary")

        if register_button:
            if email and full_name and password and confirm_password:
                if password != confirm_password:
                    st.error("❌ Passwords do not match.")
                elif len(password) < 6:
                    st.error("❌ Password must be at least 6 characters long.")
                elif user_exists(email):
                    st.error("❌ User with this email already exists.")
                else:
                    # Prepare additional data for teachers
                    additional_data = {}
                    if user_role == "Teacher/Tutor":
                        additional_data = {
                            'subjects': subjects if 'subjects' in locals() else [],
                            'institution': institution if 'institution' in locals() else ""
                        }

                    if create_user(email, full_name, password, user_role, additional_data):
                        st.success("✅ Account created successfully! Please login.")
                    else:
                        st.error("❌ Failed to create account. Please try again.")
            else:
                st.error("❌ Please fill in all fields.")

def authenticate_user(email, password):
    """Authenticate user with email and password."""
    try:
        # Load users from file
        users = load_users()

        if email in users:
            stored_password_hash = users[email]['password']
            input_password_hash = hash_password(password)

            if stored_password_hash == input_password_hash:
                # Create session
                create_session(email, users[email])
                return True

        return False

    except Exception as e:
        st.error(f"Authentication error: {str(e)}")
        return False

def create_user(email, full_name, password, role="Student", additional_data=None):
    """Create a new user account."""
    try:
        # Load existing users
        users = load_users()

        # Hash password
        password_hash = hash_password(password)

        # Add new user
        user_data = {
            'password': password_hash,
            'full_name': full_name,
            'role': role,
            'created_at': datetime.now().isoformat()
        }

        # Add additional data for teachers
        if additional_data:
            user_data.update(additional_data)

        users[email] = user_data

        # Save users
        save_users(users)
        return True

    except Exception as e:
        st.error(f"Error creating user: {str(e)}")
        return False

def create_session(email, user_data):
    """Create user session."""
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())[:8]

        # Session data
        session_data = {
            'user_info': {
                'email': email,
                'full_name': user_data.get('full_name', ''),
                'user_id': session_id,
                'role': user_data.get('role', 'Student'),
                'subjects': user_data.get('subjects', []),
                'institution': user_data.get('institution', '')
            },
            'login_time': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        }

        # Save session
        save_session(session_id, session_data)

        # Store in Streamlit session state
        st.session_state.authenticated = True
        st.session_state.user_info = session_data['user_info']
        st.session_state.session_id = session_id

    except Exception as e:
        st.error(f"Error creating session: {str(e)}")

def load_users():
    """Load users from file."""
    users_file = "users.json"

    if os.path.exists(users_file):
        try:
            with open(users_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    return {}

def save_users(users):
    """Save users to file."""
    users_file = "users.json"

    try:
        with open(users_file, 'w') as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        st.error(f"Error saving users: {str(e)}")

def save_session(session_id, session_data):
    """Save session data."""
    session_file = f"session_{session_id}.json"

    try:
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
    except Exception as e:
        st.error(f"Error saving session: {str(e)}")

def user_exists(email):
    """Check if user exists."""
    users = load_users()
    return email in users

def hash_password(password):
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def logout_user():
    """Logout current user."""
    # Clear session state
    if 'authenticated' in st.session_state:
        del st.session_state.authenticated
    if 'user_info' in st.session_state:
        del st.session_state.user_info
    if 'session_id' in st.session_state:
        # Remove session file
        session_file = f"session_{st.session_state.session_id}.json"
        if os.path.exists(session_file):
            try:
                os.remove(session_file)
            except Exception:
                pass
        del st.session_state.session_id

    st.rerun()