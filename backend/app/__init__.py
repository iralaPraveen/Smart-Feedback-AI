"""
Flask application factory
"""
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

def create_app():
    # Load environment variables
    load_dotenv()
    
    # Create Flask app
    app = Flask(__name__)
    
    # Enable CORS for all routes
    CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])
    
    # Load configuration
    from app.config import Config
    app.config.from_object(Config)
    
    # Register blueprints/routes
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Health check route
    @app.route('/')
    def index():
        return {
            'message': 'Feedback Analyzer Backend API',
            'status': 'running',
            'version': '1.0.0'
        }
    
    return app
