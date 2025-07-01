#!/usr/bin/env python3
"""
Configuration Module for House Crush
Handles environment-based configuration for development vs production modes.
"""

import os
from typing import Dict, Any

class Config:
    """Configuration class that handles environment-based settings."""
    
    def __init__(self):
        """Initialize configuration based on environment variables."""
        self.environment = os.getenv('FLASK_ENV', 'development').lower()
        self.is_development = self.environment in ['development', 'dev', 'debug']
        self.is_production = self.environment in ['production', 'prod']
        
        # Debug and logging settings
        self.enable_debug_logging = self.is_development
        self.enable_file_logging = self.is_development
        self.enable_debug_files = self.is_development
        self.enable_feedback_logging = self.is_development
        
        # Override with explicit environment variables if set
        if os.getenv('ENABLE_DEBUG_LOGGING') is not None:
            self.enable_debug_logging = os.getenv('ENABLE_DEBUG_LOGGING', 'false').lower() == 'true'
        
        if os.getenv('ENABLE_FILE_LOGGING') is not None:
            self.enable_file_logging = os.getenv('ENABLE_FILE_LOGGING', 'false').lower() == 'true'
        
        if os.getenv('ENABLE_DEBUG_FILES') is not None:
            self.enable_debug_files = os.getenv('ENABLE_DEBUG_FILES', 'false').lower() == 'true'
        
        if os.getenv('ENABLE_FEEDBACK_LOGGING') is not None:
            self.enable_feedback_logging = os.getenv('ENABLE_FEEDBACK_LOGGING', 'false').lower() == 'true'
    
    def get_debug_config(self) -> Dict[str, Any]:
        """Get debug configuration settings."""
        return {
            'environment': self.environment,
            'is_development': self.is_development,
            'is_production': self.is_production,
            'enable_debug_logging': self.enable_debug_logging,
            'enable_file_logging': self.enable_file_logging,
            'enable_debug_files': self.enable_debug_files,
            'enable_feedback_logging': self.enable_feedback_logging
        }
    
    def should_log_debug(self) -> bool:
        """Check if debug logging should be enabled."""
        return self.enable_debug_logging
    
    def should_save_debug_files(self) -> bool:
        """Check if debug files should be saved."""
        return self.enable_debug_files
    
    def should_log_feedback(self) -> bool:
        """Check if feedback logging should be enabled."""
        return self.enable_feedback_logging
    
    def should_log_to_files(self) -> bool:
        """Check if logging to files should be enabled."""
        return self.enable_file_logging

# Global configuration instance
config = Config() 