import os
import uuid
import pickle
import time
from datetime import datetime, timedelta
from config import Config

class SessionManager:
    """Manage user sessions and uploaded data"""
    
    def __init__(self):
        self.sessions = {}
        
    def create_session(self, filename, filepath, dataframe):
        """Create a new session for uploaded file"""
        session_id = str(uuid.uuid4())
        
        session_data = {
            'id': session_id,
            'filename': filename,
            'filepath': filepath,
            'dataframe': dataframe,
            'created_at': datetime.now(),
            'last_accessed': datetime.now(),
            'cache': {}
        }
        
        self.sessions[session_id] = session_data
        
        # Save session to disk for persistence
        self._save_session(session_id)
        
        return session_id
    
    def get_session(self, session_id):
        """Retrieve session data"""
        if session_id in self.sessions:
            self.sessions[session_id]['last_accessed'] = datetime.now()
            return self.sessions[session_id]
        
        # Try loading from disk
        return self._load_session(session_id)
    
    def update_session(self, session_id, key, value):
        """Update session data"""
        if session_id in self.sessions:
            self.sessions[session_id][key] = value
            self.sessions[session_id]['last_accessed'] = datetime.now()
            self._save_session(session_id)
            return True
        return False
    
    def cache_result(self, session_id, cache_key, result):
        """Cache analysis results to avoid recomputation"""
        if session_id in self.sessions:
            self.sessions[session_id]['cache'][cache_key] = result
            self._save_session(session_id)
    
    def get_cached_result(self, session_id, cache_key):
        """Retrieve cached result"""
        if session_id in self.sessions:
            return self.sessions[session_id]['cache'].get(cache_key)
        return None
    
    def delete_session(self, session_id):
        """Delete a session and clean up files"""
        if session_id in self.sessions:
            filepath = self.sessions[session_id].get('filepath')
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
            
            cache_path = os.path.join(Config.CACHE_FOLDER, f"{session_id}.pkl")
            if os.path.exists(cache_path):
                os.remove(cache_path)
            
            del self.sessions[session_id]
    
    def cleanup_old_sessions(self):
        """Remove sessions older than timeout period"""
        current_time = datetime.now()
        timeout_delta = timedelta(seconds=Config.SESSION_TIMEOUT)
        
        expired_sessions = []
        for session_id, session_data in self.sessions.items():
            if current_time - session_data['last_accessed'] > timeout_delta:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.delete_session(session_id)
        
        return len(expired_sessions)
    
    def _save_session(self, session_id):
        """Save session to disk"""
        try:
            cache_path = os.path.join(Config.CACHE_FOLDER, f"{session_id}.pkl")
            with open(cache_path, 'wb') as f:
                pickle.dump(self.sessions[session_id], f)
        except Exception as e:
            print(f"Error saving session: {e}")
    
    def _load_session(self, session_id):
        """Load session from disk"""
        try:
            cache_path = os.path.join(Config.CACHE_FOLDER, f"{session_id}.pkl")
            if os.path.exists(cache_path):
                with open(cache_path, 'rb') as f:
                    session_data = pickle.load(f)
                    self.sessions[session_id] = session_data
                    return session_data
        except Exception as e:
            print(f"Error loading session: {e}")
        return None

# Global session manager instance
session_manager = SessionManager()
