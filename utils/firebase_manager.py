
import streamlit as st
import json
import os
from datetime import datetime
import hashlib

try:
    from config.firebase_config import (
        get_firebase_config, 
        get_auth_settings, 
        get_database_settings,
        validate_config
    )
    FIREBASE_CONFIG_AVAILABLE = True
except ImportError:
    FIREBASE_CONFIG_AVAILABLE = False

try:
    import firebase_admin
    from firebase_admin import credentials, firestore, auth
    import pyrebase
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

class FirebaseManager:
    """Manages Firebase authentication and database operations."""
    
    def __init__(self):
        self.firebase_app = None
        self.auth_client = None
        self.db = None
        self.firebase_config = None
        self.initialized = False
        
    def initialize(self):
        """Initialize Firebase connection."""
        if not FIREBASE_CONFIG_AVAILABLE:
            st.error("❌ Firebase configuration file not found. Please create config/firebase_config.py")
            return False
            
        if not FIREBASE_AVAILABLE:
            st.error("❌ Firebase libraries not installed. Please install firebase-admin and pyrebase4")
            return False
        
        # Validate configuration
        is_valid, message = validate_config()
        if not is_valid:
            st.error(f"❌ Firebase configuration error: {message}")
            st.info("Please edit config/firebase_config.py with your Firebase project details")
            return False
            
        try:
            self.firebase_config = get_firebase_config()
            
            # Initialize Pyrebase for authentication
            pyrebase_config = {
                "apiKey": self.firebase_config["WEB_API_KEY"],
                "authDomain": self.firebase_config["AUTH_DOMAIN"],
                "databaseURL": self.firebase_config.get("DATABASE_URL", ""),
                "projectId": self.firebase_config["PROJECT_ID"],
                "storageBucket": self.firebase_config["STORAGE_BUCKET"],
                "messagingSenderId": self.firebase_config["MESSAGING_SENDER_ID"],
                "appId": self.firebase_config["APP_ID"]
            }
            
            firebase = pyrebase.initialize_app(pyrebase_config)
            self.auth_client = firebase.auth()
            
            # Initialize Firebase Admin for Firestore
            if not firebase_admin._apps:
                # For development, use the service account key or application default credentials
                try:
                    # Try to use application default credentials first
                    cred = credentials.ApplicationDefault()
                    firebase_admin.initialize_app(cred, {
                        'projectId': self.firebase_config["PROJECT_ID"]
                    })
                except Exception as e:
                    # If no service account available, show instructions
                    st.warning("⚠️ Firebase Admin credentials not found. Some features may be limited.")
                    st.info("For full functionality, set up a service account key file.")
                    # Continue without admin SDK for basic auth functionality
            
            self.db = firestore.client()
            self.initialized = True
            return True
            
        except Exception as e:
            st.error(f"❌ Failed to initialize Firebase: {str(e)}")
            return False
    
    def create_user(self, email, password, full_name, role="Student", **kwargs):
        """Create a new user with Firebase Authentication."""
        if not self.initialized:
            return False, "Firebase not initialized"
            
        try:
            # Create user with Firebase Auth
            user = self.auth_client.create_user_with_email_and_password(email, password)
            user_id = user['localId']
            
            # Store additional user data in Firestore
            user_data = {
                'email': email,
                'full_name': full_name,
                'role': role,
                'created_at': datetime.now().isoformat(),
                'user_id': user_id,
                **kwargs
            }
            
            db_settings = get_database_settings()
            self.db.collection(db_settings["USERS_COLLECTION"]).document(user_id).set(user_data)
            
            return True, user_id
            
        except Exception as e:
            return False, str(e)
    
    def authenticate_user(self, email, password):
        """Authenticate user with email and password."""
        if not self.initialized:
            return False, "Firebase not initialized"
            
        try:
            user = self.auth_client.sign_in_with_email_and_password(email, password)
            user_id = user['localId']
            
            # Get user data from Firestore
            db_settings = get_database_settings()
            user_doc = self.db.collection(db_settings["USERS_COLLECTION"]).document(user_id).get()
            
            if user_doc.exists:
                user_data = user_doc.to_dict()
                return True, user_data
            else:
                return False, "User data not found"
                
        except Exception as e:
            return False, str(e)
    
    def get_user_progress(self, user_id):
        """Get user progress data."""
        if not self.initialized:
            return {}
            
        try:
            db_settings = get_database_settings()
            progress_doc = self.db.collection(db_settings["PROGRESS_COLLECTION"]).document(user_id).get()
            return progress_doc.to_dict() if progress_doc.exists else {}
        except Exception as e:
            st.error(f"Error getting user progress: {str(e)}")
            return {}
    
    def save_user_progress(self, user_id, progress_data):
        """Save user progress data."""
        if not self.initialized:
            return False
            
        try:
            db_settings = get_database_settings()
            self.db.collection(db_settings["PROGRESS_COLLECTION"]).document(user_id).set(
                progress_data, merge=True
            )
            return True
        except Exception as e:
            st.error(f"Error saving user progress: {str(e)}")
            return False

# Global Firebase manager instance
firebase_manager = FirebaseManager()
