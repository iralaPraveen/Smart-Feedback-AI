"""
AI Service for feedback summarization using Google AI with dynamic theme extraction
"""

import google.generativeai as genai
from app.config import Config
import logging
import time
import re
from collections import Counter
import string

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
            combined_feedback = "\n".join([
                f"Review {i+1}: {fb}"
                for i, fb in enumerate(feedback_list)
            ])
            
            prompt = f"""
You are an expert feedback analyzer. Analyze the following customer reviews/feedback:

FEEDBACK DATA:
{combined_feedback}

Please provide a comprehensive analysis with the following sections:

## Overall Summary
Provide a brief overview of the feedback.

## Key Positive Points
List the main positive aspects mentioned by customers.

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
        """Get detailed sentiment analysis with EXPLICIT percentages"""
        if not feedback_list:
            return "No feedback data for sentiment analysis."
        
        try:
            combined_feedback = "\n".join([
                f"{i+1}. {fb}"
                for i, fb in enumerate(feedback_list)
            ])
            
            prompt = f"""
Analyze the sentiment and themes of this customer feedback data:

{combined_feedback}

IMPORTANT: Start your response with EXACT sentiment percentages in this format:
Positive: XX%
Negative: XX%
Neutral: XX%

Example:
Positive: 65%
Negative: 25%
Neutral: 10%

Then provide:

## Most Common Positive Themes
List the top positive themes mentioned.

## Most Common Negative Themes
List the top concerns or complaints.

## Key Issues Mentioned
List any problems or issues reported.

## Quality Assessment
Feedback about the overall quality/experience.

## Overall Mood
Describe the general mood of the customers.

Make sure the percentages add up to 100% and are clearly formatted as shown above.
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

    def _extract_sentiment_percentage(self, text, sentiment):
        """Enhanced sentiment percentage extraction with multiple patterns"""
        try:
            import re
            
            # Multiple regex patterns to catch different formats
            patterns = [
                sentiment + r"\s*:\s*(\d+)%",           # "Positive: 65%"
                sentiment + r"\s*-\s*(\d+)%",           # "Positive - 65%"
                sentiment + r"\s*=\s*(\d+)%",           # "Positive = 65%"
                sentiment + r"\s*is\s*(\d+)%",          # "Positive is 65%"
                r"(\d+)%\s*" + sentiment,               # "65% Positive"
                sentiment + r".*?(\d+)%",               # "Positive feedback: 65%"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    percentage = int(match.group(1))
                    logger.info(f"✅ Found {sentiment}: {percentage}%")
                    return percentage
            
            # Try to find percentage near sentiment word
            sentiment_index = text.lower().find(sentiment.lower())
            if sentiment_index != -1:
                nearby_text = text[max(0, sentiment_index-30):sentiment_index+50]
                percentage_match = re.search(r'(\d+)%', nearby_text)
                if percentage_match:
                    percentage = int(percentage_match.group(1))
                    logger.info(f"✅ Found nearby {sentiment}: {percentage}%")
                    return percentage
            
            logger.warning(f"❌ No {sentiment} percentage found in text")
            return 0
            
        except Exception as e:
            logger.error(f"Error extracting {sentiment} percentage: {e}")
            return 0

    def _extract_themes_dynamically(self, feedback_list):
        """
        DYNAMIC THEME EXTRACTION - Works for ANY type of review
        """
        try:
            # First try AI-assisted extraction
            ai_themes = self._extract_themes_with_ai(feedback_list)
            if ai_themes:
                return ai_themes
            
            # Fallback to simple NLP extraction
            return self._extract_themes_simple_nlp(feedback_list)
            
        except Exception as e:
            logger.error(f"Error in dynamic theme extraction: {e}")
            return {}

    def _extract_themes_with_ai(self, feedback_list):
        """Use AI to extract themes dynamically"""
        try:
            combined_feedback = "\n".join(feedback_list)
            
            prompt = f"""
Analyze the following customer feedback and extract the top 8 key themes or topics mentioned.

FEEDBACK:
{combined_feedback}

For each theme, provide the theme name and approximate count of mentions.

Format your response EXACTLY as:
Service: 8
Quality: 6
Price: 4
Staff: 3

Focus on the most frequently mentioned aspects, issues, or topics. Use simple 1-2 word theme names.
"""
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                themes = {}
                lines = response.text.strip().split('\n')
                
                for line in lines:
                    if ':' in line:
                        try:
                            parts = line.split(':')
                            if len(parts) == 2:
                                theme = parts[0].strip()
                                count_str = parts[1].strip()
                                
                                # Extract number from count string
                                count_match = re.search(r'\d+', count_str)
                                if count_match:
                                    count = int(count_match.group())
                                    themes[theme] = count
                        except:
                            continue
                
                # Sort by count and return top themes
                sorted_themes = dict(sorted(themes.items(), key=lambda x: x[1], reverse=True)[:8])
                logger.info(f"✅ AI extracted themes: {sorted_themes}")
                return sorted_themes
            
            logger.warning("AI theme extraction failed - empty response")
            return {}
            
        except Exception as e:
            logger.error(f"Error in AI theme extraction: {e}")
            return {}

    def _extract_themes_simple_nlp(self, feedback_list):
        """Simple NLP-based theme extraction as fallback"""
        try:
            # Combine all feedback
            combined_text = ' '.join(feedback_list).lower()
            
            # Remove punctuation and split into words
            translator = str.maketrans('', '', string.punctuation)
            clean_text = combined_text.translate(translator)
            words = clean_text.split()
            
            # Common stop words to exclude
            stop_words = {
                'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
                'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had',
                'do', 'does', 'did', 'will', 'would', 'should', 'could', 'can', 'may', 'might',
                'must', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us',
                'them', 'my', 'your', 'his', 'our', 'their', 'this', 'that', 'these', 'those',
                'very', 'really', 'quite', 'just', 'also', 'too', 'so', 'more', 'most', 'much',
                'many', 'some', 'any', 'all', 'each', 'every', 'both', 'either', 'neither'
            }
            
            # Filter meaningful words
            meaningful_words = [
                word for word in words 
                if word not in stop_words 
                and len(word) > 2 
                and word.isalpha()
            ]
            
            # Count word frequencies
            word_freq = Counter(meaningful_words)
            
            # Get top 8 most common words as themes
            top_themes = dict(word_freq.most_common(8))
            
            # Capitalize theme names for consistency
            formatted_themes = {theme.title(): count for theme, count in top_themes.items()}
            
            logger.info(f"✅ Simple NLP extracted themes: {formatted_themes}")
            return formatted_themes
            
        except Exception as e:
            logger.error(f"Error in simple NLP theme extraction: {e}")
            return {}

    def get_structured_analysis(self, feedback_list):
        """
        Get structured analysis perfect for frontend charts - WORKS FOR ANY REVIEW TYPE
        """
        if not feedback_list:
            return {
                'success': False,
                'total_feedback': 0,
                'summary': 'No feedback data to analyze',
                'sentiment_description': 'No feedback available for analysis',
                'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0},
                'key_themes': {},
                'statistics': {
                    'total_responses': 0,
                    'positive_count': 0,
                    'negative_count': 0,
                    'neutral_count': 0
                },
                'suggestions': ['No suggestions available']
            }
        
        try:
            # Get AI-generated analysis
            summary = self.summarize_feedback(feedback_list)
            sentiment_description = self.get_sentiment_breakdown(feedback_list)
            
            # Extract sentiment percentages
            sentiment_distribution = {
                'positive': self._extract_sentiment_percentage(sentiment_description, 'Positive'),
                'negative': self._extract_sentiment_percentage(sentiment_description, 'Negative'),
                'neutral': self._extract_sentiment_percentage(sentiment_description, 'Neutral')
            }
            
            # Validate sentiment percentages
            total_percentage = sum(sentiment_distribution.values())
            if total_percentage == 0:
                # Smart fallback based on simple sentiment analysis
                sentiment_distribution = self._generate_fallback_sentiment(feedback_list)
                logger.warning("Using intelligent fallback sentiment distribution")
            elif total_percentage < 80 or total_percentage > 120:
                # Normalize if percentages don't add up correctly
                factor = 100 / total_percentage if total_percentage > 0 else 1
                sentiment_distribution = {
                    k: int(v * factor) for k, v in sentiment_distribution.items()
                }
                logger.info(f"Normalized sentiment distribution: {sentiment_distribution}")
            
            # DYNAMIC THEME EXTRACTION - works for any type of review
            key_themes = self._extract_themes_dynamically(feedback_list)
            
            # Generate actionable suggestions
            suggestions = self._generate_suggestions(sentiment_distribution, key_themes, feedback_list)
            
            # Calculate statistics
            statistics = {
                'total_responses': len(feedback_list),
                'positive_count': int(len(feedback_list) * sentiment_distribution['positive'] / 100),
                'negative_count': int(len(feedback_list) * sentiment_distribution['negative'] / 100),
                'neutral_count': int(len(feedback_list) * sentiment_distribution['neutral'] / 100)
            }
            
            logger.info("✅ Structured analysis completed successfully")
            return {
                'success': True,
                'total_feedback': len(feedback_list),
                'summary': summary,
                'sentiment_description': sentiment_description,
                'sentiment_distribution': sentiment_distribution,
                'key_themes': key_themes,
                'statistics': statistics,
                'suggestions': suggestions
            }
            
        except Exception as e:
            logger.error(f"Error in structured analysis: {e}")
            return {
                'success': False,
                'total_feedback': len(feedback_list) if feedback_list else 0,
                'summary': f'Analysis error: {str(e)}',
                'sentiment_description': f'Error in sentiment analysis: {str(e)}',
                'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0},
                'key_themes': {},
                'statistics': {
                    'total_responses': len(feedback_list) if feedback_list else 0,
                    'positive_count': 0,
                    'negative_count': 0,
                    'neutral_count': 0
                },
                'suggestions': ['Analysis failed - please try again']
            }

    def _generate_fallback_sentiment(self, feedback_list):
        """Generate intelligent fallback sentiment when AI extraction fails"""
        try:
            positive_words = {'good', 'great', 'excellent', 'amazing', 'love', 'perfect', 'best', 'wonderful', 'fantastic', 'awesome', 'satisfied', 'happy', 'pleased'}
            negative_words = {'bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'disappointing', 'poor', 'unsatisfied', 'angry', 'frustrated', 'broken', 'failed'}
            
            combined_text = ' '.join(feedback_list).lower()
            words = re.findall(r'\b\w+\b', combined_text)
            
            positive_count = sum(1 for word in words if word in positive_words)
            negative_count = sum(1 for word in words if word in negative_words)
            neutral_count = len(feedback_list) - positive_count - negative_count
            
            total = len(feedback_list)
            if total == 0:
                return {'positive': 50, 'negative': 30, 'neutral': 20}
            
            return {
                'positive': max(10, int(positive_count * 100 / total)),
                'negative': max(5, int(negative_count * 100 / total)),
                'neutral': max(5, 100 - int((positive_count + negative_count) * 100 / total))
            }
            
        except:
            return {'positive': 60, 'negative': 25, 'neutral': 15}

    def _generate_suggestions(self, sentiment_dist, themes, feedback_list):
        """Generate actionable suggestions based on analysis - GENERIC for any review type"""
        suggestions = []
        
        # Sentiment-based suggestions
        negative_pct = sentiment_dist.get('negative', 0)
        positive_pct = sentiment_dist.get('positive', 0)
        
        if negative_pct > 30:
            suggestions.append("🚨 URGENT: Address negative feedback issues immediately")
            suggestions.append("📞 Implement customer satisfaction improvement plan")
        elif negative_pct > 15:
            suggestions.append("⚠️ Monitor negative feedback trends and take corrective action")
        
        if positive_pct > 70:
            suggestions.append("✅ Leverage positive feedback for marketing testimonials")
            suggestions.append("🎉 Maintain current quality standards that customers love")
        elif positive_pct < 40:
            suggestions.append("📈 Focus on improving overall customer satisfaction")
        
        # Theme-based suggestions (top 3 themes)
        top_themes = list(themes.keys())[:3] if themes else []
        for theme in top_themes:
            theme_lower = theme.lower()
            if 'service' in theme_lower:
                suggestions.append(f"🎯 Prioritize improving {theme.lower()} based on feedback")
            elif 'quality' in theme_lower:
                suggestions.append("🔧 Implement quality control improvements")
            elif 'price' in theme_lower or 'cost' in theme_lower:
                suggestions.append("💰 Review pricing strategy and value proposition")
            else:
                suggestions.append(f"📋 Address {theme.lower()} concerns mentioned frequently")
        
        # Default suggestions
        if len(suggestions) < 3:
            suggestions.extend([
                "📊 Set up regular feedback monitoring dashboard",
                "🔄 Create systematic follow-up process with customers",
                "📈 Track improvement metrics over time"
            ])
        
        return suggestions[:6]  # Return max 6 suggestions
