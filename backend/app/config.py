"""
Configuration settings
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # API Keys
    GOOGLE_AI_API_KEY = os.getenv('GOOGLE_AI_API_KEY')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    
    # Google Sheets API Settings
    SHEETS_API_SCOPE = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    
    # AI Model Settings
    AI_MODEL_NAME = 'gemini-2.5-flash'
    MAX_TOKENS = 1000
    
    @staticmethod
    def validate_config():
        """Validate required configuration"""
        required_vars = ['GOOGLE_AI_API_KEY', 'GOOGLE_API_KEY']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
