"""
API Routes
"""
from flask import Blueprint, request, jsonify
from app.services.sheets_service import GoogleSheetsService
from app.services.ai_service import FeedbackSummarizer
from app.config import Config
import logging
import pandas as pd


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
            'message': 'Feedback Analyzer Backend is running',
            'services': {
                'google_sheets': 'connected',
                'ai_service': 'connected'
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@api_bp.route('/analyze-feedback', methods=['POST'])
def analyze_feedback():
    """
    Analyze feedback from Google Sheets
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
        
        logger.info(f"Analyzing feedback from sheet: {spreadsheet_id}")
        
        # Fetch feedback from Google Sheets
        feedback_data = sheets_service.get_feedback_data(spreadsheet_id, range_name)
        
        if not feedback_data:
            return jsonify({
                'error': 'No feedback data found in the specified sheet/range'
            }), 400
        
        logger.info(f"Found {len(feedback_data)} feedback responses")
        
        # Generate AI summary
        summary = summarizer.summarize_feedback(feedback_data)
        sentiment_analysis = summarizer.get_sentiment_breakdown(feedback_data)
        
        # Prepare response
        response_data = {
            'success': True,
            'timestamp': str(pd.Timestamp.now()),
            'total_responses': len(feedback_data),
            'summary': summary,
            'sentiment_analysis': sentiment_analysis,
            'sample_feedback': feedback_data[:3],  # First 3 for preview
            'metadata': {
                'spreadsheet_id': spreadsheet_id,
                'range_analyzed': range_name
            }
        }
        
        logger.info("Analysis completed successfully")
        return jsonify(response_data), 200
        
    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({
            'error': 'An unexpected error occurred',
            'details': str(e)
        }), 500

@api_bp.route('/test-connection', methods=['GET'])
def test_connection():
    """Test Google Sheets connection"""
    try:
        # Test with a sample spreadsheet ID (you can replace with a test sheet)
        test_result = sheets_service.test_connection()
        return jsonify({
            'google_sheets_connection': 'success' if test_result else 'failed',
            'ai_service': 'ready'
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Connection test failed',
            'details': str(e)
        }), 500
