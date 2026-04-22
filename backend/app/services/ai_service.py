import google.generativeai as genai
from app.config import Config
from app.services.nlp_processor import NLPProcessor
from app.services.clustering import FeedbackClusterer
from app.services.local_llm_service import LocalLLMService
import logging
import numpy as np

logger = logging.getLogger(__name__)


# ================= MAIN CLASS =================
class FeedbackSummarizer:
    def __init__(self):
        try:
            genai.configure(api_key=Config.GOOGLE_AI_API_KEY)
            self.model = genai.GenerativeModel(Config.AI_MODEL_NAME)

            self.local_llm = LocalLLMService()

            self.nlp_processor = NLPProcessor()
            self.clusterer = FeedbackClusterer()

            logger.info("✅ Optimized AI Service initialized (NO CACHE MODE)")

        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise

    # ================= SAFE CALL =================
    def _safe_call(self, prompt):
        """
        Try Gemini → fallback to Local LLM if quota exceeded
        """
        try:
            response = self.model.generate_content(prompt)

            if response and response.text:
                return response.text

        except Exception as e:
            err = str(e)

            if "429" in err:
                logger.warning("⚠️ Gemini quota exceeded → switching to LOCAL LLM")

                local_result = self.local_llm.generate(prompt)

                if local_result:
                    return local_result

                logger.error("❌ Local LLM also failed")

            else:
                logger.error(f"Gemini error: {e}")

        return None

    # ================= MAIN PIPELINE =================
    def get_structured_analysis(self, feedback_list):

        if not feedback_list:
            return self._empty_response()

        try:
            logger.info(f"🚀 Processing {len(feedback_list)} feedbacks")

            # STEP 1: NLP
            cleaned_texts, embeddings = self.nlp_processor.preprocess_feedback(feedback_list)

            keyword_results = self.nlp_processor.extract_keywords(feedback_list, top_n=3)
            keybert_themes = self.nlp_processor.aggregate_keywords(keyword_results)
            tfidf_themes = self.nlp_processor.extract_keywords_tfidf(feedback_list, top_n=10)

            key_themes = self._merge_themes(keybert_themes, tfidf_themes)

            # STEP 2: CLUSTER
            cluster_result = self.clusterer.cluster_feedback(embeddings, feedback_list)
            clusters = cluster_result["clusters"]

            # STEP 3: COMPRESS
            compressed_clusters = self._compress_clusters(clusters)

            # STEP 4: AI CALL (Gemini → Local fallback)
            final_summary = self._generate_summary_from_compressed(
                compressed_clusters, key_themes, len(feedback_list)
            )

            result = {
                "success": True,
                "total_feedback": int(len(feedback_list)),
                "summary": final_summary,
                "key_themes": key_themes,
                "cluster_info": compressed_clusters,
            }

            result = self._convert_numpy_types(result)

            logger.info("✅ Analysis completed successfully")
            return result

        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            return self._empty_response()

    # ================= CLUSTER COMPRESSION =================
    def _compress_clusters(self, clusters):

        TOP_K = 3
        compressed = {}

        for cid, feedbacks in clusters.items():

            samples = feedbacks[:TOP_K]
            combined = " ".join(samples).lower()

            if any(w in combined for w in ["slow", "bad", "issue", "problem"]):
                sentiment = "negative"
            elif any(w in combined for w in ["good", "great", "fast", "excellent"]):
                sentiment = "positive"
            else:
                sentiment = "mixed"

            compressed[str(cid)] = {
                "size": int(len(feedbacks)),
                "examples": samples,
                "sentiment": sentiment
            }

        return compressed

    # ================= SUMMARY =================
    def _generate_summary_from_compressed(self, clusters, themes, total):

        cluster_lines = []

        for cid, info in clusters.items():
            cluster_lines.append(
                f"Cluster {cid} ({info['size']} feedback): {info['sentiment']} sentiment"
            )

        prompt = f"""
You are analyzing customer feedback.

Clusters:
{chr(10).join(cluster_lines)}

Top themes: {", ".join(list(themes.keys())[:5])}

Write a concise business summary (6-7 lines).
"""

        result = self._safe_call(prompt)

        if result:
            return result

        return self._generate_basic_summary(clusters, themes, total)

    # ================= BASIC FALLBACK =================
    def _generate_basic_summary(self, clusters, themes, total):
        top_themes = ", ".join(list(themes.keys())[:3])

        return (
            f"Analysis of {total} feedbacks shows {len(clusters)} major groups. "
            f"Key themes include {top_themes}. "
            f"Overall sentiment varies across clusters. "
            f"Focus on improving frequently mentioned issues."
        )

    # ================= UTILS =================
    def _merge_themes(self, keybert, tfidf):
        merged = {}

        for k, v in keybert.items():
            merged[k] = int(v)

        for k, v in tfidf.items():
            merged[k] = int(v) if k not in merged else int((merged[k] + v) // 2)

        return dict(sorted(merged.items(), key=lambda x: x[1], reverse=True)[:10])

    def _convert_numpy_types(self, obj):
        if isinstance(obj, dict):
            return {str(k): self._convert_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(i) for i in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj

    def _empty_response(self):
        return {
            "success": False,
            "total_feedback": 0,
            "summary": "No feedback available",
            "key_themes": {},
            "cluster_info": {}
        }