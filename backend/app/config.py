"""
Configuration settings for Feedback Analyzer
Optimized for Docker deployment
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration class"""
    
    # Flask Settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    
    # API Keys (Backward compatible with both naming conventions)
    GOOGLE_AI_API_KEY = os.getenv('GOOGLE_AI_API_KEY')
    GOOGLE_SHEETS_API_KEY = os.getenv('GOOGLE_SHEETS_API_KEY') or os.getenv('GOOGLE_API_KEY')
    GOOGLE_API_KEY = GOOGLE_SHEETS_API_KEY
    
    # Google Sheets API Settings
    SHEETS_API_SCOPE = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    
    # AI Model Settings
    AI_MODEL_NAME = os.getenv('AI_MODEL_NAME', 'gemini-2.5-flash')
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '1000'))
    
    # CORS Settings (important for Docker)
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Server Settings
    HOST = os.getenv('HOST', '0.0.0.0')  # Important for Docker
    PORT = int(os.getenv('PORT', '8000'))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        required_vars = {
            'GOOGLE_AI_API_KEY': cls.GOOGLE_AI_API_KEY,
            'GOOGLE_SHEETS_API_KEY': cls.GOOGLE_SHEETS_API_KEY
        }
        
        missing_vars = [name for name, value in required_vars.items() if not value]
        
        if missing_vars:
            raise ValueError(
                f"❌ Missing required environment variables: {', '.join(missing_vars)}\n"
                f"Please check your .env file or environment variables."
            )
        
        return True
    
    @classmethod
    def get_config_summary(cls):
        """Get a summary of current configuration (safe for logging)"""
        return {
            'flask_env': cls.FLASK_ENV,
            'debug': cls.DEBUG,
            'host': cls.HOST,
            'port': cls.PORT,
            'ai_model': cls.AI_MODEL_NAME,
            'max_tokens': cls.MAX_TOKENS,
            'cors_origins': cls.CORS_ORIGINS,
            'google_ai_configured': bool(cls.GOOGLE_AI_API_KEY),
            'google_sheets_configured': bool(cls.GOOGLE_SHEETS_API_KEY)
        }
