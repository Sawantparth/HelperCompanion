import streamlit as st
import json
import os
from datetime import datetime

def is_authenticated():
    """Check if user is authenticated."""
    # First check if already authenticated in current session
    if 'authenticated' in st.session_state and st.session_state.authenticated:
        if 'session_id' in st.session_state:
            session_data = load_session(st.session_state.session_id)
            if session_data:
                update_session_activity(st.session_state.session_id)
                return True
    
    # Check for existing valid session files (auto-login)
    if 'session_id' not in st.session_state:
        # Look for recent session files
        import os
        import glob
        from datetime import datetime, timedelta
        
        session_files = glob.glob("session_*.json")
        
        for session_file in session_files:
            try:
                # Check if session is recent (within 30 days)
                file_time = os.path.getmtime(session_file)
                if datetime.now().timestamp() - file_time < 30 * 24 * 3600:  # 30 days
                    
                    session_id = session_file.replace('session_', '').replace('.json', '')
                    session_data = load_session(session_id)
                    
                    if session_data and 'user_info' in session_data:
                        # Auto-login with existing session
                        st.session_state.authenticated = True
                        st.session_state.user_info = session_data['user_info']
                        st.session_state.session_id = session_id
                        update_session_activity(session_id)
                        return True
            except Exception:
                continue
    
    return False

def get_current_user():
    """Get current authenticated user info."""
    if is_authenticated() and 'user_info' in st.session_state:
        return st.session_state.user_info
    return None

def load_session(session_id):
    """Load session data from file."""
    session_file = f"session_{session_id}.json"
    
    if os.path.exists(session_file):
        try:
            with open(session_file, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    
    return None

def update_session_activity(session_id):
    """Update session last activity timestamp."""
    session_file = f"session_{session_id}.json"
    
    if os.path.exists(session_file):
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            session_data['last_activity'] = datetime.now().isoformat()
            
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
                
        except Exception as e:
            print(f"Error updating session activity: {e}")

def require_auth():
    """Decorator-like function to require authentication."""
    if not is_authenticated():
        st.error("Please log in to access this feature.")
        st.stop()
    
    return True

def get_user_id():
    """Get current user ID."""
    user_info = get_current_user()
    if user_info:
        return user_info.get('user_id', 'default')
    return 'default'

def get_user_role():
    """Get current user role."""
    user_info = get_current_user()
    if user_info:
        return user_info.get('role', 'Student')
    return 'Student'

def is_teacher():
    """Check if current user is a teacher/tutor."""
    return get_user_role() == "Teacher/Tutor"

def is_student():
    """Check if current user is a student."""
    return get_user_role() == "Student"

def get_user_subjects():
    """Get subjects taught by current teacher."""
    user_info = get_current_user()
    if user_info and is_teacher():
        return user_info.get('subjects', [])
    return []

def require_teacher_role():
    """Require teacher role for access."""
    if not is_teacher():
        st.error("Access denied. This feature is only available for Teachers/Tutors.")
        st.stop()
    return True

def cleanup_old_sessions():
    """Clean up old session files (older than 7 days)."""
    try:
        current_time = datetime.now().timestamp()
        for filename in os.listdir('.'):
            if filename.startswith('session_') and filename.endswith('.json'):
                file_path = filename
                file_time = os.path.getmtime(file_path)
                
                # Delete files older than 7 days
                if current_time - file_time > 7 * 24 * 3600:
                    os.remove(file_path)
                    
    except Exception as e:
        print(f"Error cleaning up sessions: {e}")

def init_auth_system():
    """Initialize authentication system."""
    # Clean up old sessions on startup
    cleanup_old_sessions()
    
    # Ensure session state is properly initialized
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
