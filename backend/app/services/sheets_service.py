"""
Google Sheets Service - Using API Key authentication
"""
import pandas as pd
import requests
import logging
from app.config import Config

logger = logging.getLogger(__name__)

class GoogleSheetsService:
    def __init__(self):
        self.api_key = Config.GOOGLE_API_KEY
        self.base_url = "https://sheets.googleapis.com/v4/spreadsheets"
    
    def get_feedback_data(self, spreadsheet_id, range_name='Sheet1!A:B'):
        """
        Fetch feedback data from Google Sheets using API key
        """
        try:
            # Construct the API URL
            url = f"{self.base_url}/{spreadsheet_id}/values/{range_name}"
            params = {
                'key': self.api_key,
                'majorDimension': 'ROWS'
            }
            
            logger.info(f"Fetching data from sheet: {spreadsheet_id}, range: {range_name}")
            
            # Make the API request
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            values = data.get('values', [])
            
            if not values:
                logger.warning("No data found in the specified range")
                return []
            
            # Process the data
            feedback_list = []
            
            # Assuming first row contains headers
            if len(values) > 1:
                headers = values[0]
                
                # Find feedback column (case insensitive)
                feedback_col_index = None
                for i, header in enumerate(headers):
                    if 'feedback' in header.lower():
                        feedback_col_index = i
                        break
                
                if feedback_col_index is None:
                    # If no 'feedback' column found, use the last column
                    feedback_col_index = len(headers) - 1
                    logger.info(f"No 'feedback' column found, using column index: {feedback_col_index}")
                
                # Extract feedback data
                for row in values[1:]:  # Skip header row
                    if len(row) > feedback_col_index and row[feedback_col_index].strip():
                        feedback_list.append(row[feedback_col_index].strip())
            
            logger.info(f"Successfully extracted {len(feedback_list)} feedback entries")
            return feedback_list
            
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 403:
                logger.error("Access denied. Check if the sheet is publicly accessible or API key has proper permissions")
                raise ValueError("Access denied. Make sure the Google Sheet is publicly accessible.")
            elif response.status_code == 404:
                logger.error("Spreadsheet not found")
                raise ValueError("Spreadsheet not found. Check the spreadsheet ID.")
            else:
                logger.error(f"HTTP error occurred: {http_err}")
                raise ValueError(f"Failed to fetch data from Google Sheets: {http_err}")
        except Exception as e:
            logger.error(f"Error fetching feedback data: {e}")
            raise ValueError(f"Error accessing Google Sheets: {str(e)}")
    
    def test_connection(self):
        """Test Google Sheets API connection"""
        try:
            # Test with a simple API call
            url = "https://sheets.googleapis.com/v4/spreadsheets"
            params = {'key': self.api_key}
            
            response = requests.get(url, params=params)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_sheet_info(self, spreadsheet_id):
        """Get basic information about the spreadsheet"""
        try:
            url = f"{self.base_url}/{spreadsheet_id}"
            params = {
                'key': self.api_key,
                'fields': 'properties.title,sheets.properties'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error getting sheet info: {e}")
            return None
