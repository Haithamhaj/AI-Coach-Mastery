import firebase_admin
from firebase_admin import credentials, firestore, auth
import streamlit as st
import os
import json

# Initialize Firebase App
def initialize_firebase():
    # Check if already initialized
    if not firebase_admin._apps:
        try:
            # Load credentials from file
            cred = credentials.Certificate("firebase_key.json")
            firebase_admin.initialize_app(cred)
            return True
        except Exception as e:
            st.error(f"Failed to initialize Firebase: {e}")
            return False
    return True

def verify_login(email, password):
    """
    Verify login using Firestore 'users' collection and hashed passwords.
    This is a custom implementation since Admin SDK cannot verify passwords directly without Web API Key.
    """
    import hashlib
    
    try:
        db = firestore.client()
        # Query for user with this email
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', email).limit(1).stream()
        
        user_doc = None
        for doc in query:
            user_doc = doc
            break
            
        if not user_doc:
            return None
            
        user_data = user_doc.to_dict()
        stored_hash = user_data.get('password_hash')
        
        # Hash the provided password
        input_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if input_hash == stored_hash:
            # Return user info including ID
            user_info = user_data
            user_info['uid'] = user_doc.id
            return user_info
        else:
            return None
            
    except Exception as e:
        print(f"Login error: {e}")
        return None

def create_user(email, password, username):
    """
    Create a new user with hashed password in Firestore.
    """
    import hashlib
    
    try:
        db = firestore.client()
        
        # Check if email already exists
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', email).limit(1).stream()
        for _ in query:
            return {"error": "Email already exists"}
            
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Create user document
        new_user_ref = db.collection('users').document()
        user_data = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'created_at': firestore.SERVER_TIMESTAMP,
            'role': 'coach'
        }
        new_user_ref.set(user_data)
        
        # Return user info
        user_data['uid'] = new_user_ref.id
        return user_data
        
    except Exception as e:
        return {"error": str(e)}

# Database Functions
def save_session(user_id, session_data):
    try:
        db = firestore.client()
        # Add timestamp
        session_data['created_at'] = firestore.SERVER_TIMESTAMP
        db.collection('sessions').add(session_data)
        return True
    except Exception as e:
        print(f"Error saving session: {e}")
        return False

def get_user_history(user_id):
    try:
        db = firestore.client()
        docs = db.collection('sessions').where('user_id', '==', user_id).order_by('created_at', direction=firestore.Query.DESCENDING).stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        print(f"Error getting history: {e}")
        return []
