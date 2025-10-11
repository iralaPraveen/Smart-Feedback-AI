"""
NLP Preprocessing Module
Handles text cleaning, embeddings, and keyword extraction
"""

import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sentence_transformers import SentenceTransformer
from keybert import KeyBERT
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter
import numpy as np
import logging

logger = logging.getLogger(__name__)

class NLPProcessor:
    def __init__(self):
        """Initialize NLP tools and models"""
        try:
            # Initialize NLTK tools
            self.stop_words = set(stopwords.words('english'))
            self.lemmatizer = WordNetLemmatizer()
            
            # Load embedding model (lightweight and fast)
            logger.info("Loading sentence embedding model...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize KeyBERT for keyword extraction
            self.kw_model = KeyBERT(model=self.embedding_model)
            
            logger.info("✅ NLP Processor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize NLP Processor: {e}")
            raise
    
    def preprocess_feedback(self, feedback_list):
        """
        Clean and preprocess feedback texts
        Returns: cleaned texts and their embeddings
        """
        if not feedback_list:
            return [], np.array([])
        
        try:
            cleaned_texts = []
            
            for text in feedback_list:
                # 1. Lowercase
                text = text.lower()
                
                # 2. Remove special characters & numbers
                text = re.sub(r'[^a-z\s]', '', text)
                
                # 3. Tokenize
                words = text.split()
                
                # 4. Remove stopwords
                words = [w for w in words if w not in self.stop_words and len(w) > 2]
                
                # 5. Lemmatize
                words = [self.lemmatizer.lemmatize(w) for w in words]
                
                # 6. Join back
                cleaned_text = ' '.join(words)
                cleaned_texts.append(cleaned_text if cleaned_text else text)
            
            # Generate embeddings for all cleaned feedback
            logger.info(f"Generating embeddings for {len(cleaned_texts)} texts...")
            embeddings = self.embedding_model.encode(cleaned_texts, show_progress_bar=False)
            
            logger.info(f"✅ Preprocessing complete: {len(cleaned_texts)} texts processed")
            return cleaned_texts, embeddings
            
        except Exception as e:
            logger.error(f"Error in preprocessing: {e}")
            return [], np.array([])
    
    def extract_keywords(self, feedback_list, top_n=5):
        """
        Extract keywords using KeyBERT
        """
        try:
            results = []
            
            for feedback in feedback_list:
                if not feedback or len(feedback.strip()) < 5:
                    results.append({
                        'feedback': feedback,
                        'keywords': []
                    })
                    continue
                
                # Extract keywords with scores
                keywords = self.kw_model.extract_keywords(
                    feedback, 
                    keyphrase_ngram_range=(1, 2),
                    stop_words='english',
                    top_n=top_n
                )
                
                # Extract only keyword strings
                keywords_only = [kw for kw, score in keywords]
                
                results.append({
                    'feedback': feedback,
                    'keywords': keywords_only
                })
            
            logger.info(f"✅ Keywords extracted from {len(results)} feedbacks")
            return results
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []
    
    def aggregate_keywords(self, keyword_results):
        """
        Aggregate and count keyword frequency across all feedback
        """
        try:
            all_keywords = []
            
            for item in keyword_results:
                all_keywords.extend(item.get('keywords', []))
            
            # Count frequency
            keyword_freq = Counter(all_keywords)
            
            # Return top keywords as dict
            top_keywords = dict(keyword_freq.most_common(15))
            
            logger.info(f"✅ Aggregated {len(top_keywords)} unique keywords")
            return top_keywords
            
        except Exception as e:
            logger.error(f"Error aggregating keywords: {e}")
            return {}
    
    def extract_keywords_tfidf(self, feedback_list, top_n=10):
        """
        Alternative: Extract keywords using TF-IDF
        """
        try:
            if not feedback_list or len(feedback_list) == 0:
                return {}
            
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                max_features=30,
                ngram_range=(1, 2),
                stop_words='english',
                min_df=1
            )
            
            # Fit and transform
            tfidf_matrix = vectorizer.fit_transform(feedback_list)
            feature_names = vectorizer.get_feature_names_out()
            
            # Get average TF-IDF scores
            avg_scores = np.mean(tfidf_matrix.toarray(), axis=0)
            
            # Create keyword-score pairs
            keyword_scores = list(zip(feature_names, avg_scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Return top keywords as dict
            top_keywords = {
                kw.title(): int(score * 100) 
                for kw, score in keyword_scores[:top_n]
                if score > 0
            }
            
            logger.info(f"✅ TF-IDF extracted {len(top_keywords)} keywords")
            return top_keywords
            
        except Exception as e:
            logger.error(f"Error in TF-IDF extraction: {e}")
            return {}
