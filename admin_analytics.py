"""
Admin Analytics - Analytics and statistics for admin dashboard
"""
from firebase_admin import firestore
from datetime import datetime, timedelta
import pandas as pd

class AdminAnalytics:
    def __init__(self):
        self.db = firestore.client()
    
    def get_total_users(self):
        """Get total number of registered users"""
        try:
            users = self.db.collection('users').stream()
            return len(list(users))
        except Exception as e:
            print(f"Error getting total users: {e}")
            return 0
    
    def get_active_users(self, days=30):
        """Get number of active users in the last N days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            users = self.db.collection('users').stream()
            active_count = 0
            
            for user in users:
                user_data = user.to_dict()
                last_activity = user_data.get('usage_stats', {}).get('last_activity')
                
                if last_activity and last_activity > cutoff_date:
                    active_count += 1
            
            return active_count
        except Exception as e:
            print(f"Error getting active users: {e}")
            return 0
    
    def get_total_stats(self):
        """Get overall platform statistics"""
        try:
            # Total users
            total_users = self.get_total_users()
            
            # Total sessions
            sessions = list(self.db.collection('sessions_summary').stream())
            total_sessions = len(sessions)
            
            # Total tokens and cost
            users = self.db.collection('users').stream()
            total_tokens = 0
            total_cost = 0
            
            for user in users:
                user_data = user.to_dict()
                stats = user_data.get('usage_stats', {})
                total_tokens += stats.get('total_tokens', 0)
                total_cost += stats.get('total_cost', 0)
            
            # Active users (last 30 days)
            active_users = self.get_active_users(30)
            
            return {
                'total_users': total_users,
                'active_users_30d': active_users,
                'total_sessions': total_sessions,
                'total_tokens': total_tokens,
                'total_cost': total_cost
            }
        except Exception as e:
            print(f"Error getting total stats: {e}")
            return {}
    
    def get_token_usage_by_service(self):
        """Get token usage breakdown by service type"""
        try:
            logs = self.db.collection('api_usage_logs').stream()
            
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
    
    def get_top_users(self, limit=10):
        """Get top users by token usage"""
        try:
            users = self.db.collection('users').stream()
            
            user_list = []
            for user in users:
                user_data = user.to_dict()
                email = user_data.get('email', user.id)
                stats = user_data.get('usage_stats', {})
                
                user_list.append({
                    'email': email,
                    'total_sessions': stats.get('total_sessions', 0),
                    'total_tokens': stats.get('total_tokens', 0),
                    'total_cost': stats.get('total_cost', 0),
                    'last_activity': stats.get('last_activity')
                })
            
            # Sort by tokens descending
            user_list.sort(key=lambda x: x['total_tokens'], reverse=True)
            
            return user_list[:limit]
        except Exception as e:
            print(f"Error getting top users: {e}")
            return []
    
    def get_user_progress(self, user_id):
        """Get user's progress over time (scores)"""
        try:
            sessions = self.db.collection('sessions_summary')\
                             .where('user_id', '==', user_id)\
                             .order_by('timestamp')\
                             .stream()
            
            progress_data = []
            
            for session in sessions:
                data = session.to_dict()
                progress_data.append({
                    'timestamp': data.get('timestamp'),
                    'score': data.get('score', 0),
                    'session_type': data.get('session_type', 'unknown'),
                    'competencies_observed': data.get('competencies_observed', 0)
                })
            
            return progress_data
        except Exception as e:
            print(f"Error getting user progress: {e}")
            return []
    
    def get_usage_over_time(self, days=30):
        """Get token usage over time"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            logs = self.db.collection('api_usage_logs')\
                         .where('timestamp', '>=', cutoff_date)\
                         .stream()
            
            daily_usage = {}
            
            for log in logs:
                data = log.to_dict()
                timestamp = data.get('timestamp')
                
                if timestamp:
                    date_key = timestamp.strftime('%Y-%m-%d')
                    tokens = data.get('tokens_used', {}).get('total', 0)
                    cost = data.get('cost_estimate', 0)
                    
                    if date_key not in daily_usage:
                        daily_usage[date_key] = {'tokens': 0, 'cost': 0, 'calls': 0}
                    
                    daily_usage[date_key]['tokens'] += tokens
                    daily_usage[date_key]['cost'] += cost
                    daily_usage[date_key]['calls'] += 1
            
            return daily_usage
        except Exception as e:
            print(f"Error getting usage over time: {e}")
            return {}
    
    def search_users(self, search_term):
        """Search users by email"""
        try:
            users = self.db.collection('users').stream()
            
            results = []
            search_lower = search_term.lower()
            
            for user in users:
                user_data = user.to_dict()
                email = user_data.get('email', user.id)
                
                if search_lower in email.lower():
                    results.append({
                        'email': email,
                        'role': user_data.get('role', 'user'),
                        'created_at': user_data.get('created_at'),
                        'usage_stats': user_data.get('usage_stats', {})
                    })
            
            return results
        except Exception as e:
            print(f"Error searching users: {e}")
            return []


# Singleton instance
_analytics_instance = None

def get_admin_analytics():
    """Get or create analytics instance"""
    global _analytics_instance
    if _analytics_instance is None:
        _analytics_instance = AdminAnalytics()
    return _analytics_instance
