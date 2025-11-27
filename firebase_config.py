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
        
        # Create user document with email as ID
        new_user_ref = db.collection('users').document(email)
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

def get_user_profile(email):
    """
    Fetch user profile data (name, title, etc.) from Firestore.
    """
    try:
        db = firestore.client()
        doc_ref = db.collection('users').document(email)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as e:
        print(f"Error fetching profile: {e}")
        return None

def update_user_profile(email, profile_data):
    """
    Update user profile fields.
    """
    try:
        db = firestore.client()
        doc_ref = db.collection('users').document(email)
        # Use set with merge=True to update existing fields or create if missing
        doc_ref.set(profile_data, merge=True)
        return True
    except Exception as e:
        print(f"Error updating profile: {e}")
        return False

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

def save_arcade_result(user_id, score, level, details):
    """
    Save Arcade Mode game results to Firestore.
    """
    try:
        db = firestore.client()
        data = {
            'user_id': user_id,
            'score': score,
            'level': level,
            'details': details,
            'type': 'arcade',
            'created_at': firestore.SERVER_TIMESTAMP
        }
        db.collection('arcade_results').add(data)
        return True
    except Exception as e:
        print(f"Error saving arcade result: {e}")
        return False

def get_user_stats(user_id):
    """
    Aggregate user statistics for the profile page.
    """
    try:
        db = firestore.client()
        
        # 1. Fetch Training Sessions
        sessions_ref = db.collection('sessions').where('user_id', '==', user_id)
        sessions = [doc.to_dict() for doc in sessions_ref.stream()]
        
        # 2. Fetch Arcade Results
        arcade_ref = db.collection('arcade_results').where('user_id', '==', user_id)
        arcade_games = [doc.to_dict() for doc in arcade_ref.stream()]
        
        # Calculate Stats
        total_sessions = len(sessions)
        total_arcade_games = len(arcade_games)
        
        # Calculate Total Hours (assuming avg 30 mins per session if duration not tracked)
        # In a real app, we'd track actual duration.
        total_hours = (total_sessions * 0.5) + (total_arcade_games * 0.1) # 6 mins per arcade game
        
        # Calculate Avg Score (from sessions that have a score)
        scores = [s.get('compliance_percentage', 0) for s in sessions if 'compliance_percentage' in s]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Calculate Arcade Points
        total_arcade_points = sum([g.get('score', 0) for g in arcade_games])
        
        # Determine Rank
        # Determine Rank
        rank_key = "rank_novice"
        if total_arcade_points > 1000: rank_key = "rank_mcc"
        elif total_arcade_points > 500: rank_key = "rank_pcc"
        elif total_arcade_points > 200: rank_key = "rank_acc"
        
        return {
            'total_sessions': total_sessions,
            'total_hours': round(total_hours, 1),
            'avg_score': round(avg_score, 1),
            'arcade_games': total_arcade_games,
            'arcade_points': total_arcade_points,
            'rank_key': rank_key,
            'recent_sessions': sorted(sessions, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
        }
        
    except Exception as e:
        print(f"Error getting user stats: {e}")
        return None
