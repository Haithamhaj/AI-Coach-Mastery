"""
Token Tracker - Track API usage and costs for Gemini API
"""
import firebase_admin
from firebase_admin import firestore
from datetime import datetime
import streamlit as st

class TokenTracker:
    def __init__(self):
        try:
            if firebase_admin._apps:
                self.db = firestore.client()
            else:
                self.db = None
        except Exception as e:
            print(f"TokenTracker init error: {e}")
            self.db = None
    
    def log_api_call(self, user_id, service_type, tokens_used, model="gemini-flash", session_id=None):
        """
        Log an API call with token usage
        
        Args:
            user_id: User email
            service_type: "pcc_analysis", "full_session", "training", "ethics_check"
            tokens_used: Dict with 'input', 'output', 'total'
            model: "gemini-flash" or "gemini-pro"
            session_id: Optional session identifier
        """
        try:
            if not self.db:
                return False
                
            # Calculate cost
            cost = self.calculate_cost(tokens_used.get('total', 0), model)
            
            # Create log entry
            log_entry = {
                'user_id': user_id,
                'service_type': service_type,
                'timestamp': firestore.SERVER_TIMESTAMP,
                'tokens_used': tokens_used,
                'cost_estimate': cost,
                'model': model
            }
            
            if session_id:
                log_entry['session_id'] = session_id
            
            # Save to Firestore
            self.db.collection('api_usage_logs').add(log_entry)
            
            # Update user's total usage
            self._update_user_usage(user_id, tokens_used.get('total', 0), cost)
            
            return True
        except Exception as e:
            print(f"Error logging API call: {e}")
            return False
    
    def calculate_cost(self, total_tokens, model="gemini-flash"):
        """
        Calculate cost based on token count and model
        
        Pricing (approximate):
        - Gemini Flash: $0.001 per 1K input tokens, $0.004 per 1K output tokens
        - Gemini Pro: $0.0167 per 1K input tokens, $0.0667 per 1K output tokens
        
        Using average for total tokens
        """
        if model == "gemini-pro":
            # Average cost per 1K tokens
            cost_per_1k = 0.042  # Average of input and output
        else:  # gemini-flash
            cost_per_1k = 0.0025  # Average of input and output
        
        return (total_tokens / 1000) * cost_per_1k
    
    def _update_user_usage(self, user_id, tokens, cost):
        """Update user's total usage statistics"""
        if not self.db:
            return
            
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                current_stats = user_doc.to_dict().get('usage_stats', {})
                
                user_ref.update({
                    'usage_stats': {
                        'total_tokens': current_stats.get('total_tokens', 0) + tokens,
                        'total_cost': current_stats.get('total_cost', 0) + cost,
                        'last_activity': firestore.SERVER_TIMESTAMP
                    }
                })
            else:
                # Create user document if doesn't exist
                user_ref.set({
                    'email': user_id,
                    'role': 'user',
                    'created_at': firestore.SERVER_TIMESTAMP,
                    'usage_stats': {
                        'total_tokens': tokens,
                        'total_cost': cost,
                        'last_activity': firestore.SERVER_TIMESTAMP
                    }
                })
        except Exception as e:
            print(f"Error updating user usage: {e}")
    
    def get_user_usage(self, user_id):
        """Get total usage for a specific user"""
        if not self.db:
            return {}
            
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                return user_doc.to_dict().get('usage_stats', {})
            return {}
        except Exception as e:
            print(f"Error getting user usage: {e}")
            return {}
    
    def get_user_usage_by_service(self, user_id):
        """Get usage breakdown by service type for a user"""
        if not self.db:
            return {}
            
        try:
            logs = self.db.collection('api_usage_logs')\
                         .where('user_id', '==', user_id)\
                         .stream()
            
            usage_by_service = {}
            
            for log in logs:
                data = log.to_dict()
                service = data.get('service_type', 'unknown')
                tokens = data.get('tokens_used', {}).get('total', 0)
                cost = data.get('cost_estimate', 0)
                
                if service not in usage_by_service:
                    usage_by_service[service] = {
                        'tokens': 0,
                        'cost': 0,
                        'count': 0
                    }
                
                usage_by_service[service]['tokens'] += tokens
                usage_by_service[service]['cost'] += cost
                usage_by_service[service]['count'] += 1
            
            return usage_by_service
        except Exception as e:
            print(f"Error getting usage by service: {e}")
            return {}
    
    def log_session_summary(self, user_id, session_type, score, duration, competencies_observed, tokens_used):
        """Log a session summary for analytics"""
        if not self.db:
            return False
            
        try:
            summary = {
                'user_id': user_id,
                'session_type': session_type,
                'timestamp': firestore.SERVER_TIMESTAMP,
                'score': score,
                'duration': duration,
                'competencies_observed': competencies_observed,
                'tokens_used': tokens_used
            }
            
            self.db.collection('sessions_summary').add(summary)
            
            # Update user's session count
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                current_stats = user_doc.to_dict().get('usage_stats', {})
                user_ref.update({
                    'usage_stats.total_sessions': current_stats.get('total_sessions', 0) + 1
                })
            
            return True
        except Exception as e:
            print(f"Error logging session summary: {e}")
            return False


# Singleton instance
_tracker_instance = None

def get_token_tracker():
    """Get or create token tracker instance"""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = TokenTracker()
    return _tracker_instance
