#!/usr/bin/env python3
"""
Feedback Logger Module
Handles user feedback logging for the House Crush application.
"""

import os
import json
from datetime import datetime
from typing import Dict, Optional
from config import config

# Create tmp directory for feedback files only in development
tmp_dir = "tmp"
if config.should_log_to_files() and not os.path.exists(tmp_dir):
    os.makedirs(tmp_dir)

class FeedbackLogger:
    def __init__(self, log_file: str = os.path.join(tmp_dir, 'user_feedback.log'), 
                 json_file: str = os.path.join(tmp_dir, 'feedback_data.json')):
        """
        Initialize the feedback logger.
        
        Args:
            log_file: Path to the text log file (now in tmp directory)
            json_file: Path to the JSON data file (now in tmp directory)
        """
        self.log_file = log_file
        self.json_file = json_file
        self.feedback_data = self._load_feedback_data()
    
    def _load_feedback_data(self) -> Dict:
        """Load existing feedback data from JSON file."""
        if not config.should_save_json_files():
            return {
                'total_feedback': 0,
                'feedback_entries': [],
                'last_updated': datetime.now().isoformat()
            }
        
        try:
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            if config.should_log_debug():
                print(f"Error loading feedback data: {e}")
        
        return {
            'total_feedback': 0,
            'feedback_entries': [],
            'last_updated': datetime.now().isoformat()
        }
    
    def _save_feedback_data(self):
        """Save feedback data to JSON file."""
        if not config.should_save_json_files():
            return
        
        try:
            self.feedback_data['last_updated'] = datetime.now().isoformat()
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(self.feedback_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            if config.should_log_debug():
                print(f"Error saving feedback data: {e}")
    
    def log_feedback(self, feedback: str, user_info: Optional[Dict] = None) -> bool:
        """
        Log user feedback.
        
        Args:
            feedback: The feedback text from the user
            user_info: Optional user information (IP, user agent, etc.)
            
        Returns:
            bool: True if feedback was logged successfully, False otherwise
        """
        if not feedback or not feedback.strip():
            return False
        
        timestamp = datetime.now()
        
        # Prepare feedback entry
        entry = {
            'id': self.feedback_data['total_feedback'] + 1,
            'timestamp': timestamp.isoformat(),
            'feedback': feedback.strip(),
            'user_info': user_info or {}
        }
        
        try:
            # Log to text file only in development
            if config.should_log_feedback() and config.should_log_to_files():
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {feedback.strip()}\n")
            
            # Add to JSON data
            self.feedback_data['feedback_entries'].append(entry)
            self.feedback_data['total_feedback'] += 1
            
            # Save JSON data only in development
            if config.should_save_json_files():
                self._save_feedback_data()
            
            if config.should_log_debug():
                print(f"✅ Feedback logged successfully (ID: {entry['id']})")
            return True
            
        except Exception as e:
            if config.should_log_debug():
                print(f"❌ Error logging feedback: {e}")
            return False
    
    def get_feedback_stats(self) -> Dict:
        """Get feedback statistics."""
        return {
            'total_feedback': self.feedback_data['total_feedback'],
            'last_updated': self.feedback_data['last_updated'],
            'recent_feedback': self.feedback_data['feedback_entries'][-10:] if self.feedback_data['feedback_entries'] else []
        }
    
    def get_all_feedback(self) -> list:
        """Get all feedback entries."""
        return self.feedback_data['feedback_entries']
    
    def clear_feedback(self) -> bool:
        """Clear all feedback data."""
        if not config.should_save_json_files():
            return True
        
        try:
            # Clear text log only in development
            if config.should_log_to_files():
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    f.write(f"# Feedback log cleared on {datetime.now().isoformat()}\n")
            
            # Reset JSON data
            self.feedback_data = {
                'total_feedback': 0,
                'feedback_entries': [],
                'last_updated': datetime.now().isoformat()
            }
            self._save_feedback_data()
            
            if config.should_log_debug():
                print("✅ Feedback data cleared successfully")
            return True
            
        except Exception as e:
            if config.should_log_debug():
                print(f"❌ Error clearing feedback: {e}")
            return False

# Global instance
feedback_logger = FeedbackLogger()

def log_user_feedback(feedback: str, user_info: Optional[Dict] = None) -> bool:
    """
    Convenience function to log user feedback.
    
    Args:
        feedback: The feedback text from the user
        user_info: Optional user information
        
    Returns:
        bool: True if feedback was logged successfully
    """
    return feedback_logger.log_feedback(feedback, user_info)

def get_feedback_stats() -> Dict:
    """Get feedback statistics."""
    return feedback_logger.get_feedback_stats()

def get_all_feedback() -> list:
    """Get all feedback entries."""
    return feedback_logger.get_all_feedback()

def clear_feedback() -> bool:
    """Clear all feedback data."""
    return feedback_logger.clear_feedback() 