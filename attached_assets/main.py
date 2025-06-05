import streamlit as st
from components.file_upload import render_file_upload
from components.chat import render_chat_interface
from components.visualization import render_analysis_results
from components.progress_analytics import render_progress_analytics
from components.simple_auth import render_simple_auth
from utils.progress_tracker import ProgressTracker
from utils.simple_auth import is_authenticated
import os

# Configure Streamlit page
st.set_page_config(
    page_title="Study Companion AI",
    page_icon="📚",
    layout="wide",
    menu_items={
        'Get Help': 'https://github.com/yourusername/study-companion-ai/issues',
        'Report a bug': "https://github.com/yourusername/study-companion-ai/issues",
        'About': "Study Companion AI - Your intelligent study partner for exam preparation."
    }
)

def initialize_session_state():
    """Initialize session state variables."""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'analyzed_data' not in st.session_state:
        st.session_state.analyzed_data = None
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    if 'error_log' not in st.session_state:
        st.session_state.error_log = []
    if 'progress_tracker' not in st.session_state:
        st.session_state.progress_tracker = ProgressTracker()
    if 'api_configured' not in st.session_state:
        st.session_state.api_configured = False
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = None
    if 'firebase_configured' not in st.session_state:
        st.session_state.firebase_configured = False
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

def render_api_configuration():
    """Render API configuration section."""
    st.header("🔑 API Configuration")
    st.markdown("Please configure your AI model and API key to get started.")
    
    with st.form("api_config_form"):
        # Model selection
        col1, col2 = st.columns(2)
        
        with col1:
            model_provider = st.selectbox(
                "Select AI Model Provider:",
                ["Google Gemini", "OpenAI"]
            )
        
        with col2:
            if model_provider == "Google Gemini":
                model_version = st.selectbox(
                    "Select Model Version:",
                    ["gemini-pro", "gemini-1.5-pro", "gemini-1.5-flash"]
                )
            else:  # OpenAI
                model_version = st.selectbox(
                    "Select Model Version:",
                    ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]
                )
        
        # API key input
        if model_provider == "Google Gemini":
            api_key = st.text_input(
                "Enter your Google AI API Key:",
                type="password",
                help="Get your API key from https://makersuite.google.com/app/apikey"
            )
        else:
            api_key = st.text_input(
                "Enter your OpenAI API Key:",
                type="password", 
                help="Get your API key from https://platform.openai.com/api-keys"
            )
        
        submit_button = st.form_submit_button("Configure API", type="primary")
        
        if submit_button:
            if api_key:
                # Store configuration in session state
                st.session_state.api_key = api_key
                st.session_state.model_provider = model_provider
                st.session_state.model_version = model_version
                st.session_state.api_configured = True
                st.session_state.selected_model = f"{model_provider} - {model_version}"
                st.success(f"API configured successfully! Using {model_provider} - {model_version}")
                st.rerun()
            else:
                st.error("Please enter your API key.")

def main():
    # Initialize session state
    initialize_session_state()

    # Page header
    st.title("📚 Study Companion AI")
    st.markdown("""
    Your intelligent study partner for exam preparation. Upload your study materials 
    and get AI-powered insights and recommendations.
    """)

    # Check authentication first
    if not is_authenticated():
        authenticated = render_simple_auth()
        if not authenticated:
            return

    # Check if API is configured
    if not st.session_state.api_configured:
        render_api_configuration()
        return

    # Show current configuration and user info
    with st.sidebar:
        st.success(f"✅ Using: {st.session_state.selected_model}")
        if st.button("Change API Configuration"):
            st.session_state.api_configured = False
            st.rerun()

    try:
        # Create tabs for different functionalities
        tab1, tab2, tab3, tab4 = st.tabs([
            "📤 Upload Materials",
            "💬 Chat Assistant", 
            "📊 Analysis",
            "📈 Progress Tracking"
        ])

        with tab1:
            render_file_upload()

        with tab2:
            if not st.session_state.uploaded_files:
                st.info("Please upload study materials first to get personalized assistance.")
            else:
                render_chat_interface()

        with tab3:
            if not st.session_state.analyzed_data:
                st.info("Upload your study materials to see detailed analysis.")
            else:
                render_analysis_results()

        with tab4:
            render_progress_analytics(st.session_state.progress_tracker)

    except Exception as e:
        st.error(f"An unexpected error occurred. Please try refreshing the page. Error: {str(e)}")
        # Log error for debugging
        st.session_state.error_log.append(str(e))

if __name__ == "__main__":
    main()