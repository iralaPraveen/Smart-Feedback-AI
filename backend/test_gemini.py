"""
Test script for Gemini 2.5 Flash API connection
"""
import google.generativeai as genai
import os
from dotenv import load_dotenv

def test_gemini_connection():
    print("🔧 Testing Gemini 2.5 Flash API connection...")
    
    # Load environment variables
    load_dotenv()
    
    # Check if API key exists
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if not api_key:
        print("❌ ERROR: GOOGLE_AI_API_KEY not found in .env file")
        return False
    
    print(f"✅ API key found: {api_key[:10]}..." + "*" * 20)
    
    try:
        # Configure with your API key
        genai.configure(api_key=api_key)
        
        # Create model instance
        model = genai.GenerativeModel('gemini-2.5-flash')
        print("✅ Model instance created successfully")
        
        # Test request
        print("🚀 Sending test request...")
        response = model.generate_content("Test: Say hello and tell me you're working!")
        
        print("✅ SUCCESS! Response received:")
        print(f"📝 Response: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_gemini_connection()
    if success:
        print("\n🎉 Gemini 2.5 Flash is ready for your feedback analyzer!")
    else:
        print("\n❌ Fix the issues above before proceeding.")
