# HelperCompanion
# Firebase Configuration

This directory contains the Firebase configuration for your Study Companion AI project.

## Setup Instructions

### Step 1: Create a Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project" or select an existing project
3. Follow the setup wizard (Analytics is optional for this project)
4. Wait for project creation to complete

### Step 2: Enable Required Services
1. **Enable Authentication**:
   - In Firebase Console, go to "Authentication" in the left sidebar
   - Click "Get started"
   - Go to "Sign-in method" tab
   - Enable "Email/Password" provider
   - Click "Save"

2. **Enable Firestore Database**:
   - In Firebase Console, go to "Firestore Database" in the left sidebar
   - Click "Create database"
   - Choose "Start in test mode" (for development)
   - Select a location close to your users
   - Click "Done"

### Step 3: Get Your Firebase Configuration
1. In Firebase Console, click the gear icon (⚙️) next to "Project Overview"
2. Select "Project settings"
3. Scroll down to "Your apps" section
4. If you don't see a web app:
   - Click "Add app" button
   - Select the web icon (`</>`)
   - Enter an app nickname (e.g., "Study Companion Web")
   - Click "Register app"
5. Copy the configuration object that looks like this:
   ```javascript
   const firebaseConfig = {
     apiKey: "your-api-key-here",
     authDomain: "your-project.firebaseapp.com",
     projectId: "your-project-id",
     storageBucket: "your-project.appspot.com",
     messagingSenderId: "123456789",
     appId: "1:123456789:web:abcdef123456"
   };
   ```

### Step 4: Configure the Application
1. **Open the configuration file**:
   - Navigate to your project directory
   - Open `config/firebase_config.py` in your code editor

2. **Replace placeholder values**:
   - Find the `FIREBASE_CONFIG` dictionary
   - Replace each placeholder with your actual Firebase values:
     ```python
     FIREBASE_CONFIG = {
         "PROJECT_NAME": "Study Companion AI",  # Your project display name
         "PROJECT_ID": "your-actual-project-id",  # From firebaseConfig.projectId
         "PROJECT_NUMBER": "123456789012",  # Found in General tab of Project Settings
         "WEB_API_KEY": "your-actual-api-key",  # From firebaseConfig.apiKey
         "AUTH_DOMAIN": "your-project.firebaseapp.com",  # From firebaseConfig.authDomain
         "DATABASE_URL": "https://your-project-default-rtdb.firebaseio.com/",  # Optional
         "STORAGE_BUCKET": "your-project.appspot.com",  # From firebaseConfig.storageBucket
         "MESSAGING_SENDER_ID": "123456789012",  # From firebaseConfig.messagingSenderId
         "APP_ID": "1:123456789:web:abcdef123456"  # From firebaseConfig.appId
     }
     ```

3. **Save the file** after making all changes

### Step 5: Verify Configuration
1. **Run the application**:
   - In your terminal, run: `streamlit run main.py --server.port 5000 --server.address 127.0.0.1`
   - Or click the "Run" button in Replit

2. **Check for errors**:
   - If configuration is correct, you'll see Firebase authentication options
   - If there are errors, check the console for specific error messages
   - Common issues:
     - Mismatched project IDs
     - Invalid API keys
     - Services not enabled in Firebase Console

### Step 6: Test Authentication
1. **Create a test account**:
   - Try registering a new user with the "Create Account" option
   - Use a valid email address and password (minimum 6 characters)

2. **Verify in Firebase Console**:
   - Go to Authentication > Users in Firebase Console
   - You should see your test user listed
   - Go to Firestore Database to see user data stored

### Step 7: Optional Service Account Setup
For advanced features (like admin operations), you may need a service account:

1. **Create Service Account**:
   - In Firebase Console, go to Project Settings
   - Click "Service accounts" tab
   - Click "Generate new private key"
   - Download the JSON file

2. **Add to Replit Secrets**:
   - In Replit, go to the "Secrets" tab
   - Add a new secret named `FIREBASE_SERVICE_ACCOUNT`
   - Paste the entire JSON content as the value

### Step 8: Production Considerations
1. **Update Firestore Rules**:
   - For production, replace test mode rules with proper security rules
   - Example rules for user data protection:
   ```javascript
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       match /users/{userId} {
         allow read, write: if request.auth != null && request.auth.uid == userId;
       }
       match /user_progress/{userId} {
         allow read, write: if request.auth != null && request.auth.uid == userId;
       }
     }
   }
   ```

2. **Secure Your Configuration**:
   - Never commit real Firebase credentials to public repositories
   - Add `config/firebase_config.py` to your `.gitignore`
   - Use environment variables for production deployments

## Configuration Values Needed

- **PROJECT_NAME**: Your Firebase project display name
- **PROJECT_ID**: Your unique project ID
- **PROJECT_NUMBER**: Your project number (found in general settings)
- **WEB_API_KEY**: Your web API key
- **AUTH_DOMAIN**: Usually `{PROJECT_ID}.firebaseapp.com`
- **DATABASE_URL**: Your Realtime Database URL (if using)
- **STORAGE_BUCKET**: Usually `{PROJECT_ID}.appspot.com`
- **MESSAGING_SENDER_ID**: Same as project number
- **APP_ID**: Your web app ID

## Security Notes

- Never commit real credentials to public repositories
- Add `config/firebase_config.py` to your `.gitignore` file
- For production, use environment variables or secure secret management

## Fallback

If Firebase is not configured, the application will fall back to the local JSON-based authentication system.
