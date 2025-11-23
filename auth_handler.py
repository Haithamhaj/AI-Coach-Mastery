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
