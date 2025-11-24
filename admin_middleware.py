"""
Admin Middleware - Handle admin authentication and authorization
"""
import streamlit as st

class AdminMiddleware:
    def __init__(self):
        self._db = None
    
    @property
    def db(self):
        """Lazy load Firestore client"""
        if self._db is None:
            from firebase_admin import firestore
            self._db = firestore.client()
        return self._db
    
    def is_admin(self, user_email):
        """
        Check if a user has admin role
        
        Args:
            user_email: User's email address
            
        Returns:
            bool: True if user is admin, False otherwise
        """
        try:
            # 1. Try direct lookup (if ID is email)
            user_ref = self.db.collection('users').document(user_email)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                user_data = user_doc.to_dict()
                if user_data.get('role') == 'admin':
                    return True
            
            # 2. Fallback: Query by email field (if ID is random UID)
            users_ref = self.db.collection('users')
            query = users_ref.where('email', '==', user_email).limit(1).stream()
            
            for doc in query:
                user_data = doc.to_dict()
                if user_data.get('role') == 'admin':
                    return True
            
            return False
        except Exception as e:
            print(f"Error checking admin status: {e}")
            return False
    
    def require_admin(self):
        """
        Decorator/middleware to require admin access
        Shows error and stops execution if user is not admin
        
        Usage in Streamlit:
            admin = AdminMiddleware()
            if not admin.require_admin():
                return
        """
        if 'user_email' not in st.session_state:
            st.error("🔒 Please login to access this page")
            st.stop()
            return False
        
        user_email = st.session_state.user_email
        
        if not self.is_admin(user_email):
            st.error("⛔ Access Denied: Admin privileges required")
            st.info("This page is restricted to administrators only.")
            st.stop()
            return False
        
        return True
    
    def set_user_role(self, user_email, role):
        """
        Set a user's role (admin use only)
        
        Args:
            user_email: User's email
            role: 'admin' or 'user'
        """
        try:
            user_ref = self.db.collection('users').document(user_email)
            user_ref.update({'role': role})
            return True
        except Exception as e:
            print(f"Error setting user role: {e}")
            return False
    
    def get_user_info(self, user_email):
        """Get user information"""
        try:
            user_ref = self.db.collection('users').document(user_email)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                return user_doc.to_dict()
            return None
        except Exception as e:
            print(f"Error getting user info: {e}")
            return None
    
    def log_admin_action(self, admin_email, action, details=None):
        """Log admin actions for audit trail"""
        try:
            from firebase_admin import firestore
            log_entry = {
                'admin_email': admin_email,
                'action': action,
                'timestamp': firestore.SERVER_TIMESTAMP
            }
            
            if details:
                log_entry['details'] = details
            
            self.db.collection('admin_activity_logs').add(log_entry)
            return True
        except Exception as e:
            print(f"Error logging admin action: {e}")
            return False


# Singleton instance
_admin_instance = None

def get_admin_middleware():
    """Get or create admin middleware instance"""
    global _admin_instance
    if _admin_instance is None:
        _admin_instance = AdminMiddleware()
    return _admin_instance
