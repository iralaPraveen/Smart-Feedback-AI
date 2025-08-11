"""
AI Service for feedback summarization using Google AI
"""
import google.generativeai as genai
from app.config import Config
import logging
import time

logger = logging.getLogger(__name__)

class FeedbackSummarizer:
    def __init__(self):
        try:
            genai.configure(api_key=Config.GOOGLE_AI_API_KEY)
            self.model = genai.GenerativeModel(Config.AI_MODEL_NAME)
            logger.info("AI service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI service: {e}")
            raise
    
    def summarize_feedback(self, feedback_list):
        """Generate comprehensive summary from feedback list"""
        if not feedback_list:
            return "No feedback data to summarize."
        
        try:
            # Combine all feedback with student numbering
            combined_feedback = "\n".join([
                f"Student {i+1}: {fb}" 
                for i, fb in enumerate(feedback_list)
            ])
            
            prompt = f"""
            You are an expert feedback analyzer. Analyze the following student feedback about a speech/presentation event.

            FEEDBACK DATA:
            {combined_feedback}

            Please provide a comprehensive analysis with the following sections:

            ## Overall Summary
            Provide a brief overview of the feedback.

            ## Key Positive Points
            List the main positive aspects mentioned by students.

            ## Areas for Improvement  
            Identify the main concerns and issues raised.

            ## Common Themes
            Identify recurring topics or patterns in the feedback.

            ## Recommendations
            Suggest specific actions based on the feedback.

            ## Sentiment Overview
            Provide an overall sentiment assessment (positive/negative/mixed).

            Keep the response well-structured and actionable.
            """
            
            logger.info("Generating AI summary...")
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                logger.info("Summary generated successfully")
                return response.text
            else:
                logger.warning("Empty response from AI service")
                return "Unable to generate summary at this time."
                
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Error generating summary: {str(e)}"
    
    def get_sentiment_breakdown(self, feedback_list):
        """Get detailed sentiment analysis of feedback"""
        if not feedback_list:
            return "No feedback data for sentiment analysis."
        
        try:
            combined_feedback = "\n".join([
                f"{i+1}. {fb}" 
                for i, fb in enumerate(feedback_list)
            ])
            
            prompt = f"""
            Analyze the sentiment and themes of this student feedback data:

            {combined_feedback}

            Provide a detailed breakdown in the following format:

            ## Sentiment Distribution
            - Positive: X%
            - Negative: X%  
            - Neutral: X%

            ## Most Common Positive Themes
            List the top positive themes mentioned.

            ## Most Common Negative Themes
            List the top concerns or complaints.

            ## Technical Issues Mentioned
            List any technical problems reported.

            ## Content Quality Assessment
            Feedback about the actual content/presentation.

            ## Overall Mood
            Describe the general mood of the audience.

            Provide specific percentages and concrete examples where possible.
            """
            
            logger.info("Generating sentiment analysis...")
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                logger.info("Sentiment analysis generated successfully")
                return response.text
            else:
                logger.warning("Empty response from sentiment analysis")
                return "Unable to generate sentiment analysis at this time."
                
        except Exception as e:
            logger.error(f"Error generating sentiment analysis: {e}")
            return f"Error in sentiment analysis: {str(e)}"
    
    def get_quick_insights(self, feedback_list):
        """Get quick actionable insights"""
        try:
            combined_feedback = " ".join(feedback_list)
            
            prompt = f"""
            Based on this feedback: {combined_feedback}
            
            Provide 3-5 quick, actionable insights in bullet points.
            Focus on immediate improvements that can be made.
            """
            
            response = self.model.generate_content(prompt)
            return response.text if response and response.text else "No insights available."
            
        except Exception as e:
            logger.error(f"Error generating quick insights: {e}")
            return "Error generating insights."
