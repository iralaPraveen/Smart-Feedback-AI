"""
API Routes - Enhanced for structured AI analytics and frontend integration
"""

from flask import Blueprint, request, jsonify
from app.services.sheets_service import GoogleSheetsService
from app.services.ai_service import FeedbackSummarizer
from app.config import Config
import logging
import pandas as pd
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

# Initialize services
sheets_service = GoogleSheetsService()
summarizer = FeedbackSummarizer()

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Enhanced health check endpoint with detailed service status"""
    try:
        Config.validate_config()
        
        # Test Google Sheets connection
        sheets_status = sheets_service.test_connection()
        
        return jsonify({
            'status': 'healthy',
            'message': 'Feedback Analyzer Backend is running',
            'timestamp': datetime.utcnow().isoformat(),
            'services': {
                'google_sheets': 'connected' if sheets_status else 'disconnected',
                'ai_service': 'connected',
                'gemini_model': Config.AI_MODEL_NAME
            },
            'version': '2.0.0'
        }), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@api_bp.route('/analyze-feedback', methods=['POST'])
def analyze_feedback():
    """
    Enhanced feedback analysis with structured data for charts
    Expected payload:
    {
        "spreadsheet_id": "your_sheet_id",
        "range_name": "Sheet1!A:B" (optional)
    }
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        
        # Validate required parameters
        spreadsheet_id = data.get('spreadsheet_id')
        if not spreadsheet_id:
            return jsonify({'error': 'spreadsheet_id is required'}), 400
        
        range_name = data.get('range_name', 'Sheet1!A:B')
        
        logger.info(f"🚀 Starting analysis for spreadsheet: {spreadsheet_id}")
        
        # Fetch feedback from Google Sheets
        feedback_data = sheets_service.get_feedback_data(spreadsheet_id, range_name)
        
        if not feedback_data:
            return jsonify({
                'error': 'No feedback data found in the specified sheet/range',
                'suggestions': [
                    'Check if the spreadsheet is publicly accessible',
                    'Verify the range contains feedback data',
                    'Ensure there is data in the feedback column'
                ]
            }), 400
        
        logger.info(f"📊 Found {len(feedback_data)} feedback responses")
        
        # Use NEW structured analysis method
        analysis_results = summarizer.get_structured_analysis(feedback_data)
        
        # Prepare enhanced response for frontend charts
        response_data = {
            'success': analysis_results.get('success', True),
            'timestamp': datetime.utcnow().isoformat(),
            
            # Core analytics data
            'total_feedback': analysis_results.get('total_feedback', 0),
            'summary': analysis_results.get('summary', ''),
            'sentiment_description': analysis_results.get('sentiment_description', ''),
            
            # Chart data
            'sentiment_distribution': analysis_results.get('sentiment_distribution', {}),
            'key_themes': analysis_results.get('key_themes', {}),
            
            # Statistics for dashboard
            'statistics': analysis_results.get('statistics', {
                'total_responses': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0
            }),
            
            # Actionable insights
            'suggestions': analysis_results.get('suggestions', []),
            
            # Sample feedback for preview
            'sample_feedback': feedback_data[:3] if len(feedback_data) >= 3 else feedback_data,
            
            # Metadata
            'metadata': {
                'spreadsheet_id': spreadsheet_id,
                'range_analyzed': range_name,
                'ai_model': Config.AI_MODEL_NAME,
                'analysis_version': '2.0',
                'processing_time': 'completed'
            }
        }
        
        logger.info("✅ Analysis completed successfully")
        return jsonify(response_data), 200
        
    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        return jsonify({
            'error': str(ve),
            'type': 'validation_error',
            'timestamp': datetime.utcnow().isoformat()
        }), 400
        
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {e}", exc_info=True)
        return jsonify({
            'error': 'An unexpected error occurred during analysis',
            'details': str(e),
            'type': 'server_error',
            'timestamp': datetime.utcnow().isoformat(),
            'suggestions': [
                'Check your internet connection',
                'Verify the spreadsheet ID is correct',
                'Try again in a few moments'
            ]
        }), 500

@api_bp.route('/test-connection', methods=['GET'])
def test_connection():
    """Test Google Sheets and AI service connections"""
    try:
        # Test Google Sheets connection
        sheets_test = sheets_service.test_connection()
        
        # Test AI service (simple check)
        ai_test = True
        try:
            # Quick test with dummy data
            test_result = summarizer.get_structured_analysis(['Test feedback'])
            ai_test = test_result.get('success', False)
        except Exception:
            ai_test = False
        
        return jsonify({
            'google_sheets_connection': 'success' if sheets_test else 'failed',
            'ai_service': 'success' if ai_test else 'failed',
            'overall_status': 'ready' if (sheets_test and ai_test) else 'partial',
            'timestamp': datetime.utcnow().isoformat(),
            'details': {
                'sheets_api': 'Google Sheets API accessible' if sheets_test else 'Connection failed',
                'gemini_ai': 'Gemini AI responsive' if ai_test else 'AI service unavailable'
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return jsonify({
            'error': 'Connection test failed',
            'details': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500
