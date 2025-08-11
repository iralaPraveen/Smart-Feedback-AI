# Feedback Analyzer Backend

A Flask-based backend service that fetches feedback data from Google Sheets and provides AI-powered analysis and summarization.

## Setup

1. Install pipenv if not already installed:

2. Install dependencies:

3. Create `.env` file with your API keys

4. Run the application: if use pipenv as virtual environment(pipenv run python run.py)

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/analyze-feedback` - Analyze feedback from Google Sheets

## Requirements

- Python 3.9+
- Google AI API Key
- Google API Key with Sheets API enabled


