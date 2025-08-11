"""
Test script for Google Sheets API connection
"""
import requests
import pandas as pd
import os
from dotenv import load_dotenv

def test_google_sheets_connection():
    print("🔧 Testing Google Sheets API connection...")
    
    # Load environment variables
    load_dotenv()
    
    # Check if API key exists
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ ERROR: GOOGLE_API_KEY not found in .env file")
        return False
    
    print(f"✅ API key found: {api_key[:10]}..." + "*" * 20)
    
    # Test with a public Google Sheet (you can replace with your own)
    test_spreadsheet_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"  # Google's sample sheet
    range_name = "Class Data!A2:E"
    
    try:
        # Construct the API URL
        base_url = "https://sheets.googleapis.com/v4/spreadsheets"
        url = f"{base_url}/{test_spreadsheet_id}/values/{range_name}"
        params = {
            'key': api_key,
            'majorDimension': 'ROWS'
        }
        
        print(f"🚀 Testing with sample sheet: {test_spreadsheet_id}")
        print(f"📋 Range: {range_name}")
        
        # Make the API request
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            values = data.get('values', [])
            
            print("✅ SUCCESS! Google Sheets API is working")
            print(f"📊 Found {len(values)} rows of data")
            print("📝 Sample data (first 3 rows):")
            
            for i, row in enumerate(values[:3]):
                print(f"   Row {i+1}: {row}")
            
            return True
            
        elif response.status_code == 403:
            print("❌ ERROR: Access denied (403)")
            print("💡 Possible issues:")
            print("   - API key doesn't have Google Sheets API enabled")
            print("   - Sheet is not publicly accessible")
            print("   - Quota exceeded")
            return False
            
        elif response.status_code == 404:
            print("❌ ERROR: Sheet not found (404)")
            print("💡 Check the spreadsheet ID")
            return False
            
        else:
            print(f"❌ ERROR: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def test_your_feedback_sheet():
    """Test with your own feedback sheet"""
    load_dotenv()
    
    # Replace with your actual sheet ID
    your_sheet_id = input("Enter your Google Sheet ID (or press Enter to skip): ").strip()
    
    if not your_sheet_id:
        print("⏭️ Skipping custom sheet test")
        return
    
    api_key = os.getenv('GOOGLE_API_KEY')
    base_url = "https://sheets.googleapis.com/v4/spreadsheets"
    range_name = "Sheet1!A:B"  # Adjust based on your sheet structure
    
    try:
        url = f"{base_url}/{your_sheet_id}/values/{range_name}"
        params = {'key': api_key, 'majorDimension': 'ROWS'}
        
        print(f"🧪 Testing your feedback sheet: {your_sheet_id}")
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            values = data.get('values', [])
            
            print("✅ SUCCESS! Your feedback sheet is accessible")
            print(f"📊 Found {len(values)} rows")
            
            if values:
                print("📋 Headers:", values[0] if values else "No headers found")
                print("📝 Sample feedback entries:")
                for i, row in enumerate(values[1:4]):  # Skip header, show first 3 feedback entries
                    if len(row) > 1:
                        print(f"   Entry {i+1}: {row[1]}")  # Assuming feedback is in column B
            else:
                print("⚠️ No data found in the sheet")
                
        else:
            print(f"❌ Failed to access your sheet: HTTP {response.status_code}")
            print("💡 Make sure:")
            print("   - Sheet is shared publicly (anyone with link can view)")
            print("   - Sheet ID is correct")
            
    except Exception as e:
        print(f"❌ Error testing your sheet: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 GOOGLE SHEETS API VERIFICATION")
    print("=" * 60)
    
    # Test 1: Basic API connection
    success = test_google_sheets_connection()
    
    print("\n" + "-" * 60)
    
    # Test 2: Your feedback sheet (optional)
    if success:
        test_your_feedback_sheet()
        
    print("\n" + "=" * 60)
    if success:
        print("🎉 Google Sheets API is ready for your feedback analyzer!")
        print("👉 Next: Test your complete backend with 'python run.py'")
    else:
        print("❌ Fix the Google Sheets API issues before proceeding")
        print("💡 Check: API key, enabled APIs, and sheet permissions")
