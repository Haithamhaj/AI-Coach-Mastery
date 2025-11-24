import requests
import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")

# Firebase REST API endpoints
SIGN_IN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
SIGN_UP_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
PASSWORD_RESET_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_API_KEY}"
REFRESH_TOKEN_URL = f"https://securetoken.googleapis.com/v1/token?key={FIREBASE_API_KEY}"

def sign_in_with_email(email, password):
    """
    Sign in with email and password using Firebase REST API.
    Returns user data if successful, or error dict if failed.
    """
    try:
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        response = requests.post(SIGN_IN_URL, json=payload)
        data = response.json()
        
        if response.status_code == 200:
            return {
                "success": True,
                "idToken": data.get("idToken"),
                "refreshToken": data.get("refreshToken"),
                "email": data.get("email"),
                "localId": data.get("localId"),
                "expiresIn": data.get("expiresIn")
            }
        else:
            error_message = data.get("error", {}).get("message", "Unknown error")
            return {
                "success": False,
                "error": error_message
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def sign_up_with_email(email, password):
    """
    Create a new account with email and password.
    """
    try:
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        response = requests.post(SIGN_UP_URL, json=payload)
        data = response.json()
        
        if response.status_code == 200:
            return {
                "success": True,
                "idToken": data.get("idToken"),
                "refreshToken": data.get("refreshToken"),
                "email": data.get("email"),
                "localId": data.get("localId")
            }
        else:
            error_message = data.get("error", {}).get("message", "Unknown error")
            return {
                "success": False,
                "error": error_message
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def send_password_reset_email(email):
    """
    Send password reset email to the user.
    """
    try:
        payload = {
            "requestType": "PASSWORD_RESET",
            "email": email
        }
        
        response = requests.post(PASSWORD_RESET_URL, json=payload)
        data = response.json()
        
        if response.status_code == 200:
            return {
                "success": True,
                "message": "Password reset email sent successfully"
            }
        else:
            error_message = data.get("error", {}).get("message", "Unknown error")
            return {
                "success": False,
                "error": error_message
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def refresh_id_token(refresh_token):
    """
    Refresh the ID token using refresh token.
    """
    try:
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        
        response = requests.post(REFRESH_TOKEN_URL, json=payload)
        data = response.json()
        
        if response.status_code == 200:
            return {
                "success": True,
                "idToken": data.get("id_token"),
                "refreshToken": data.get("refresh_token"),
                "expiresIn": data.get("expires_in")
            }
        else:
            return {
                "success": False,
                "error": "Failed to refresh token"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def save_session(user_data):
    """
    Save user session to Streamlit session state.
    """
    st.session_state.user_authenticated = True
    st.session_state.user_token = user_data.get("idToken")
    st.session_state.user_email = user_data.get("email")
    st.session_state.user_id = user_data.get("localId")
    st.session_state.refresh_token = user_data.get("refreshToken")

def clear_session():
    """
    Clear user session.
    """
    if 'user_authenticated' in st.session_state:
        del st.session_state.user_authenticated
    if 'user_token' in st.session_state:
        del st.session_state.user_token
    if 'user_email' in st.session_state:
        del st.session_state.user_email
    if 'user_id' in st.session_state:
        del st.session_state.user_id
    if 'refresh_token' in st.session_state:
        del st.session_state.refresh_token

def is_authenticated():
    """
    Check if user is authenticated.
    """
    return st.session_state.get('user_authenticated', False)

def save_to_cookie(user_data, remember_me=False, cookies=None):
    """
    Save user session to browser cookie if remember_me is True.
    """
    if remember_me and cookies:
        try:
            import json
            
            # Store minimal session data
            session_data = {
                "email": user_data.get("email"),
                "user_id": user_data.get("localId"),
                "refresh_token": user_data.get("refreshToken")
            }
            
            cookies["user_session"] = json.dumps(session_data)
            cookies.save()
        except Exception as e:
            print(f"Failed to save cookie: {e}")

def load_from_cookie(cookies=None):
    """
    Load user session from browser cookie if exists.
    Returns user data or None.
    """
    try:
        if not cookies or not cookies.ready():
            return None
            
        import json
        
        session_json = cookies.get("user_session")
        if session_json:
            session_data = json.loads(session_json)
            
            # Try to refresh the token
            refresh_token = session_data.get("refresh_token")
            if refresh_token:
                result = refresh_id_token(refresh_token)
                if result.get("success"):
                    # Return refreshed session
                    return {
                        "email": session_data.get("email"),
                        "localId": session_data.get("user_id"),
                        "idToken": result.get("idToken"),
                        "refreshToken": result.get("refreshToken")
                    }
        return None
    except Exception as e:
        print(f"Failed to load cookie: {e}")
        return None

def clear_cookie(cookies=None):
    """
    Clear user session cookie.
    """
    if cookies and cookies.ready():
        try:
            if "user_session" in cookies:
                del cookies["user_session"]
                cookies.save()
        except Exception as e:
            print(f"Failed to clear cookie: {e}")


def get_google_sign_in_button_html():
    """
    Generate HTML for Google Sign-In button using Firebase UI.
    """
    firebase_config_js = f"""
    {{
        apiKey: "{FIREBASE_API_KEY}",
        authDomain: "{FIREBASE_PROJECT_ID}.firebaseapp.com",
        projectId: "{FIREBASE_PROJECT_ID}"
    }}
    """
    
    html = f"""
    <script src="https://www.gstatic.com/firebasejs/9.22.0/firebase-app-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.22.0/firebase-auth-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/ui/6.0.2/firebase-ui-auth.js"></script>
    <link type="text/css" rel="stylesheet" href="https://www.gstatic.com/firebasejs/ui/6.0.2/firebase-ui-auth.css" />
    
    <div id="firebaseui-auth-container"></div>
    
    <script>
        const firebaseConfig = {firebase_config_js};
        firebase.initializeApp(firebaseConfig);
        
        const ui = new firebaseui.auth.AuthUI(firebase.auth());
        
        ui.start('#firebaseui-auth-container', {{
            signInOptions: [
                {{
                    provider: firebase.auth.GoogleAuthProvider.PROVIDER_ID,
                    customParameters: {{
                        prompt: 'select_account'
                    }}
                }}
            ],
            callbacks: {{
                signInSuccessWithAuthResult: function(authResult) {{
                    const user = authResult.user;
                    window.parent.postMessage({{
                        type: 'FIREBASE_AUTH_SUCCESS',
                        email: user.email,
                        uid: user.uid,
                        idToken: user.accessToken
                    }}, '*');
                    return false;
                }},
                signInFailure: function(error) {{
                    console.error('Sign in failed:', error);
                    return Promise.resolve();
                }}
            }}
        }});
    </script>
    """
    return html

