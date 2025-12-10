"""
"""

import google.generativeai as genai
from app.config import Config
from app.services.nlp_processor import NLPProcessor
from app.services.clustering import FeedbackClusterer
import logging
import numpy as np

logger = logging.getLogger(__name__)

class FeedbackSummarizer:
    def __init__(self):
        try:
            # Initialize Gemini AI
            genai.configure(api_key=Config.GOOGLE_AI_API_KEY)
            self.model = genai.GenerativeModel(Config.AI_MODEL_NAME)
            
            # Initialize NLP processors
            self.nlp_processor = NLPProcessor()
            self.clusterer = FeedbackClusterer()
            
            logger.info("✅ Hybrid AI Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Hybrid AI Service: {e}")
            raise
    
    def _convert_numpy_types(self, obj):
        """
        Convert numpy types to native Python types for JSON serialization
        """
        if isinstance(obj, dict):
            return {self._convert_numpy_types(k): self._convert_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj
    
    def get_structured_analysis(self, feedback_list):
        """
        HYBRID ANALYSIS PIPELINE (Without Sentiment Analysis)
        """
        if not feedback_list:
            return self._empty_response()
        
        try:
            logger.info(f"🚀 Starting hybrid analysis for {len(feedback_list)} feedbacks")
            
            # STEP 1: Preprocessing (Clean + Embeddings)
            logger.info("Step 1: Preprocessing feedback...")
            cleaned_texts, embeddings = self.nlp_processor.preprocess_feedback(feedback_list)
            
            # STEP 2: Keyword Extraction (Parallel: KeyBERT + TF-IDF)
            logger.info("Step 2: Extracting keywords...")
            
            keyword_results = self.nlp_processor.extract_keywords(feedback_list, top_n=3)
            keybert_themes = self.nlp_processor.aggregate_keywords(keyword_results)
            tfidf_themes = self.nlp_processor.extract_keywords_tfidf(feedback_list, top_n=10)
            
            # Merge themes from both methods
            key_themes = self._merge_themes(keybert_themes, tfidf_themes)
            
            # STEP 3: Clustering
            logger.info("Step 3: Clustering feedback...")
            cluster_result = self.clusterer.cluster_feedback(embeddings, feedback_list)
            
            # STEP 4: Cluster-wise Summarization (Gemini AI)
            logger.info(f"Step 4: Generating summaries for {cluster_result['n_clusters']} clusters...")
            cluster_summaries = self._summarize_clusters(cluster_result['clusters'])
            
            # STEP 5: Final Aggregation
            logger.info("Step 5: Generating final aggregated summary...")
            final_summary = self._generate_final_summary(
                cluster_summaries, 
                key_themes, 
                len(feedback_list)
            )
            
            # STEP 6: Generate detailed suggestions
            logger.info("Step 6: Generating detailed recommendations...")
            suggestions = self._generate_suggestions(key_themes, cluster_summaries)
            
            # Calculate statistics
            statistics = {
                'total_responses': int(len(feedback_list)),
                'clusters_found': int(cluster_result['n_clusters']),
                'themes_identified': int(len(key_themes))
            }
            
            logger.info("✅ Hybrid analysis completed successfully")
            
            # Convert cluster_summaries to use string keys
            cluster_summaries_clean = {}
            for cluster_id, summary_data in cluster_summaries.items():
                cluster_summaries_clean[str(cluster_id)] = {
                    'summary': summary_data['summary'],
                    'size': int(summary_data['size']),
                    'sample_feedback': summary_data['sample_feedback']
                }
            
            result = {
                'success': True,
                'total_feedback': int(len(feedback_list)),
                'summary': final_summary,
                'key_themes': key_themes,
                'statistics': statistics,
                'suggestions': suggestions,
                'cluster_info': {
                    'n_clusters': int(cluster_result['n_clusters']),
                    'cluster_summaries': cluster_summaries_clean
                }
            }
            
            # Convert all numpy types to native Python types
            return self._convert_numpy_types(result)
            
        except Exception as e:
            logger.error(f"Error in hybrid analysis: {e}", exc_info=True)
            return self._empty_response()
    
    def _merge_themes(self, keybert_themes, tfidf_themes):
        """Merge themes from KeyBERT and TF-IDF"""
        merged = {}
        
        # Add KeyBERT themes
        for theme, count in keybert_themes.items():
            merged[theme] = int(count)
        
        # Add TF-IDF themes if not already present
        for theme, score in tfidf_themes.items():
            if theme not in merged:
                merged[theme] = int(score)
            else:
                # Average if present in both
                merged[theme] = int((merged[theme] + score) // 2)
        
        # Sort by frequency and return top 10
        sorted_themes = dict(sorted(merged.items(), key=lambda x: x[1], reverse=True)[:10])
        return sorted_themes
    
    def _summarize_clusters(self, clusters):
        """
        Generate concise summaries for each cluster using Gemini
        """
        cluster_summaries = {}
        
        for cluster_id, feedbacks in clusters.items():
            if not feedbacks:
                continue
            
            # Combine cluster feedback (limit to 20 per cluster)
            combined = "\n".join([f"- {fb}" for fb in feedbacks[:20]])
            
            prompt = f"""
Analyze this group of similar customer feedback and provide a brief summary:

{combined}

Provide a 2-3 sentence summary covering:
1. Main theme/topic of this group
2. Key points mentioned
3. Overall tone (positive/negative/neutral/mixed)

Keep it concise and factual.
"""
            
            try:
                response = self.model.generate_content(prompt)
                summary = response.text if response and response.text else "No summary available"
                cluster_summaries[int(cluster_id)] = {
                    'summary': summary,
                    'size': len(feedbacks),
                    'sample_feedback': feedbacks[0] if feedbacks else ""
                }
                logger.info(f"✅ Summarized cluster {cluster_id} ({len(feedbacks)} items)")
                
            except Exception as e:
                logger.error(f"Error summarizing cluster {cluster_id}: {e}")
                cluster_summaries[int(cluster_id)] = {
                    'summary': f"Group of {len(feedbacks)} related feedback items",
                    'size': len(feedbacks),
                    'sample_feedback': feedbacks[0] if feedbacks else ""
                }
        
        return cluster_summaries
    
    def _generate_final_summary(self, cluster_summaries, themes, total_count):
        """
        Generate CONCISE final summary (7-8 lines maximum)
        """
        # Combine cluster summaries
        cluster_texts = [
            f"Group {cid+1} ({info['size']} feedbacks): {info['summary']}"
            for cid, info in cluster_summaries.items()
        ]
        combined_clusters = "\n".join(cluster_texts)
        
        top_themes_str = ", ".join(list(themes.keys())[:5])
        
        prompt = f"""
Based on analyzing {total_count} customer feedbacks grouped into {len(cluster_summaries)} semantic clusters:

Cluster insights:
{combined_clusters}

Top themes: {top_themes_str}

Provide a CONCISE executive summary in exactly 7-8 lines (NOT MORE).
Focus on:
- Overall sentiment/trend (1-2 lines)
- Top 2-3 key findings (3-4 lines)
- Primary recommendation (1-2 lines)

Write in paragraph format, NOT bullet points. Keep it brief, professional, and actionable.
"""
        
        try:
            response = self.model.generate_content(prompt)
            summary = response.text if response and response.text else "Summary generation in progress..."
            logger.info("✅ Concise summary generated")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating final summary: {e}")
            return self._generate_fallback_summary(cluster_summaries, themes, total_count)
    
    def _generate_fallback_summary(self, cluster_summaries, themes, total_count):
        """Generate a concise fallback summary (7-8 lines)"""
        top_themes = ", ".join(list(themes.keys())[:3])
        
        # Analyze cluster summaries for overall tone
        summaries_text = " ".join([info['summary'].lower() for info in cluster_summaries.values()])
        
        # Determine overall tone
        if 'positive' in summaries_text or 'praise' in summaries_text or 'excellent' in summaries_text:
            tone = "generally positive with some areas for improvement"
        elif 'negative' in summaries_text or 'complaint' in summaries_text or 'poor' in summaries_text:
            tone = "mixed with significant concerns noted"
        else:
            tone = "varied across different aspects"
        
        # Build concise summary
        summary = f"Analyzed {total_count} customer feedbacks across {len(cluster_summaries)} thematic groups. "
        summary += f"The overall feedback is {tone}. "
        summary += f"Key themes include {top_themes}, which appear most frequently across responses. "
        
        if len(cluster_summaries) > 5:
            summary += f"The diverse range of topics indicates customers focus on multiple aspects of the experience. "
        else:
            summary += f"Feedback is concentrated around a few specific areas requiring attention. "
        
        # Add recommendation
        top_theme = list(themes.keys())[0] if themes else "identified issues"
        summary += f"Primary recommendation: Address the most frequently mentioned theme ({top_theme.lower()}) "
        summary += f"to improve customer satisfaction. Regular monitoring of feedback trends is advised for continuous improvement."
        
        return summary
    
    def _generate_suggestions(self, themes, cluster_summaries):
        """
        Generate detailed, actionable recommendations using AI analysis
        Each recommendation includes specific actions to take
        """
        try:
            # Combine all cluster summaries for context
            cluster_insights = []
            for cid, info in cluster_summaries.items():
                cluster_insights.append(f"Cluster {cid+1}: {info['summary']}")
            
            combined_insights = "\n".join(cluster_insights)
            top_themes = ", ".join(list(themes.keys())[:5])
            
            prompt = f"""
Based on customer feedback analysis with these insights:

{combined_insights}

Top themes mentioned: {top_themes}

Generate 4-5 SPECIFIC, ACTIONABLE recommendations. Each recommendation must:
1. Start with an emoji icon relevant to the action
2. Have a clear title (what to improve)
3. Include 2 lines explaining SPECIFICALLY what to do and why

Format EXACTLY as:
[Emoji] [Title]
[Line 1: Specific action to take]
[Line 2: Why it matters or additional detail]

Focus on CONCRETE actions like "reduce salt levels", "source fresher ingredients", "train staff on greeting customers", NOT generic advice like "improve food quality".

Each recommendation should be separated by a blank line.
"""
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                # Parse AI response into structured recommendations
                suggestions = self._parse_recommendations(response.text)
                logger.info(f"✅ Generated {len(suggestions)} detailed recommendations")
                return suggestions[:5]  # Return top 5
            else:
                return self._generate_fallback_suggestions(themes, cluster_summaries)
                
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return self._generate_fallback_suggestions(themes, cluster_summaries)
    
    def _parse_recommendations(self, ai_response):
        """
        Parse AI-generated recommendations into structured format
        """
        suggestions = []
        
        # Split by double newlines or numbered items
        lines = ai_response.strip().split('\n')
        current_recommendation = []
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_recommendation:
                    # Join accumulated lines into one recommendation
                    rec_text = '\n'.join(current_recommendation)
                    if len(rec_text) > 10:  # Filter out empty ones
                        suggestions.append(rec_text)
                    current_recommendation = []
            else:
                # Remove numbering if present
                line = line.lstrip('0123456789. ')
                current_recommendation.append(line)
        
        # Don't forget the last one
        if current_recommendation:
            rec_text = '\n'.join(current_recommendation)
            if len(rec_text) > 10:
                suggestions.append(rec_text)
        
        return suggestions
    
    def _generate_fallback_suggestions(self, themes, cluster_summaries):
        """
        Generate detailed fallback suggestions if AI fails
        """
        suggestions = []
        
        # Analyze cluster summaries for specific issues
        all_summaries = " ".join([info['summary'].lower() for info in cluster_summaries.values()])
        
        # Food-related suggestions
        if 'food' in themes or 'taste' in themes or 'quality' in themes:
            if 'salt' in all_summaries or 'seasoning' in all_summaries:
                suggestions.append(
                    "🍽️ Refine Food Seasoning\n"
                    "Review and standardize salt and seasoning levels across all dishes to ensure consistency.\n"
                    "Conduct regular taste tests and train kitchen staff on proper seasoning ratios to maintain quality."
                )
            elif 'fresh' in all_summaries or 'stale' in all_summaries:
                suggestions.append(
                    "🥬 Improve Ingredient Freshness\n"
                    "Source ingredients from reliable suppliers and implement daily freshness checks for all perishables.\n"
                    "Reduce inventory holding time to ensure peak freshness in all meals served to customers."
                )
            else:
                suggestions.append(
                    "👨‍🍳 Enhance Food Quality Standards\n"
                    "Establish strict quality control checkpoints in the kitchen and monitor dish consistency.\n"
                    "Provide regular chef training and recipe standardization to maintain high culinary standards."
                )
        
        # Service-related suggestions
        if 'service' in themes or 'staff' in themes or 'waiter' in themes:
            if 'rude' in all_summaries or 'unfriendly' in all_summaries:
                suggestions.append(
                    "😊 Improve Staff Courtesy Training\n"
                    "Implement comprehensive customer service workshops focusing on greeting, communication, and empathy.\n"
                    "Set clear expectations and create a recognition program to reward staff who receive positive feedback."
                )
            elif 'slow' in all_summaries or 'wait' in all_summaries:
                suggestions.append(
                    "⏱️ Reduce Service Wait Times\n"
                    "Optimize kitchen-to-table workflow and add additional staff during identified peak hours.\n"
                    "Implement a digital table management system to track and minimize customer waiting times effectively."
                )
            else:
                suggestions.append(
                    "🤝 Strengthen Customer Service Excellence\n"
                    "Conduct regular service quality audits and gather immediate customer feedback at point of service.\n"
                    "Empower frontline staff to resolve common issues on the spot without requiring manager approval."
                )
        
        # Ambiance/Place suggestions
        if 'place' in themes or 'room' in themes or 'atmosphere' in themes:
            if 'clean' in all_summaries or 'hygiene' in all_summaries:
                suggestions.append(
                    "🧹 Enhance Cleanliness Standards\n"
                    "Increase cleaning frequency and conduct hourly hygiene checks in all dining and restroom areas.\n"
                    "Display cleanliness certificates prominently and use visible cleaning schedules to build customer trust."
                )
            else:
                suggestions.append(
                    "🏠 Upgrade Ambiance and Comfort\n"
                    "Improve lighting, seating comfort, and temperature control based on direct customer feedback.\n"
                    "Add aesthetic touches like plants, art, or music to create a more welcoming and memorable atmosphere."
                )
        
        # General monitoring suggestion
        suggestions.append(
            "📊 Implement Continuous Feedback Monitoring\n"
            "Set up weekly feedback review sessions to identify emerging issues early before they escalate.\n"
            "Use trend analysis dashboards to proactively address concerns before they become widespread problems."
        )
        
        return suggestions[:5]
    
    def _empty_response(self):
        """Return empty response structure"""
        return {
            'success': False,
            'total_feedback': 0,
            'summary': 'No feedback data to analyze',
            'key_themes': {},
            'statistics': {
                'total_responses': 0,
                'clusters_found': 0,
                'themes_identified': 0
            },
            'suggestions': ['No suggestions available'],
            'cluster_info': {
                'n_clusters': 0,
                'cluster_summaries': {}
            }
        }
