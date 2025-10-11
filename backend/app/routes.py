"""
API Routes - Updated for Hybrid Analysis
"""

from flask import Blueprint, request, jsonify
from app.services.sheets_service import GoogleSheetsService
from app.services.ai_service import FeedbackSummarizer
from app.config import Config
import logging
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
    """Health check endpoint"""
    try:
        Config.validate_config()
        
        return jsonify({
            'status': 'healthy',
            'message': 'Hybrid Feedback Analyzer Backend is running',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '2.0-hybrid'
        }), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@api_bp.route('/analyze-feedback', methods=['POST'])
def analyze_feedback():
    """
    Hybrid feedback analysis endpoint
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
        
        logger.info(f"🚀 Starting hybrid analysis for spreadsheet: {spreadsheet_id}")
        
        # Fetch feedback from Google Sheets
        feedback_data = sheets_service.get_feedback_data(spreadsheet_id, range_name)
        
        if not feedback_data:
            return jsonify({
                'error': 'No feedback data found in the specified sheet/range',
                'suggestions': [
                    'Check if the spreadsheet is publicly accessible',
                    'Verify the range contains feedback data'
                ]
            }), 400
        
        logger.info(f"📊 Found {len(feedback_data)} feedback responses")
        
        # Perform hybrid analysis
        analysis_results = summarizer.get_structured_analysis(feedback_data)
        
        # Prepare response
        response_data = {
            'success': analysis_results.get('success', True),
            'timestamp': datetime.utcnow().isoformat(),
            'total_feedback': analysis_results.get('total_feedback', 0),
            'summary': analysis_results.get('summary', ''),
            'key_themes': analysis_results.get('key_themes', {}),
            'statistics': analysis_results.get('statistics', {}),
            'suggestions': analysis_results.get('suggestions', []),
            'cluster_info': analysis_results.get('cluster_info', {}),
            'metadata': {
                'spreadsheet_id': spreadsheet_id,
                'range_analyzed': range_name,
                'ai_model': Config.AI_MODEL_NAME,
                'analysis_type': 'hybrid',
                'version': '2.0'
            }
        }
        
        logger.info("✅ Analysis completed successfully")
        return jsonify(response_data), 200
        
    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        return jsonify({'error': str(ve)}), 400
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return jsonify({
            'error': 'An unexpected error occurred',
            'details': str(e)
        }), 500

@api_bp.route('/test-connection', methods=['GET'])
def test_connection():
    """Test API connections"""
    try:
        sheets_test = sheets_service.test_connection()
        
        return jsonify({
            'google_sheets': 'success' if sheets_test else 'failed',
            'ai_service': 'ready',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return jsonify({'error': str(e)}), 500

