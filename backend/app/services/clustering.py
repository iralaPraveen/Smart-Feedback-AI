"""
Clustering Module for Feedback Grouping
Uses KMeans for semantic clustering
"""

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import numpy as np
import logging

logger = logging.getLogger(__name__)

class FeedbackClusterer:
    def __init__(self):
        """Initialize clustering algorithms"""
        pass
    
    def cluster_feedback(self, embeddings, feedback_list, n_clusters=None):
        """
        Cluster feedback based on semantic embeddings using KMeans
        """
        if len(embeddings) == 0:
            return {'clusters': {}, 'labels': [], 'n_clusters': 0}
        
        try:
            # Auto-detect optimal number of clusters
            if n_clusters is None:
                n_clusters = self._optimal_clusters(embeddings)
            
            # Ensure at least 2 clusters, max 10
            n_clusters = max(2, min(n_clusters, min(10, len(feedback_list) // 3)))
            
            # Perform KMeans clustering
            labels = self._kmeans_clustering(embeddings, n_clusters)
            
            # Organize feedback by clusters
            clusters = self._organize_clusters(feedback_list, labels)
            
            logger.info(f"✅ Clustered {len(feedback_list)} feedbacks into {len(clusters)} clusters")
            
            return {
                'clusters': clusters,
                'labels': labels.tolist() if hasattr(labels, 'tolist') else labels,
                'n_clusters': len(clusters)
            }
            
        except Exception as e:
            logger.error(f"Error in clustering: {e}")
            # Fallback: single cluster
            return {
                'clusters': {0: feedback_list},
                'labels': [0] * len(feedback_list),
                'n_clusters': 1
            }
    
    def _optimal_clusters(self, embeddings):
        """Automatically determine optimal number of clusters"""
        try:
            n_samples = len(embeddings)
            
            # Rule of thumb: sqrt(n/2)
            optimal_k = int(np.sqrt(n_samples / 2))
            
            # Ensure reasonable range
            optimal_k = max(2, min(optimal_k, 8))
            
            # Try silhouette method if dataset is not too large
            if 10 <= n_samples <= 100:
                best_k = optimal_k
                best_score = -1
                
                for k in range(2, min(8, n_samples // 2)):
                    try:
                        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                        labels = kmeans.fit_predict(embeddings)
                        score = silhouette_score(embeddings, labels)
                        
                        if score > best_score:
                            best_score = score
                            best_k = k
                    except:
                        continue
                
                return best_k
            
            return optimal_k
            
        except Exception as e:
            logger.warning(f"Error in optimal cluster detection: {e}")
            return 3  # Safe default
    
    def _kmeans_clustering(self, embeddings, n_clusters):
        """Perform KMeans clustering"""
        try:
            kmeans = KMeans(
                n_clusters=n_clusters,
                random_state=42,
                n_init=10,
                max_iter=300
            )
            labels = kmeans.fit_predict(embeddings)
            return labels
            
        except Exception as e:
            logger.error(f"KMeans clustering error: {e}")
            return np.zeros(len(embeddings), dtype=int)
    
    def _organize_clusters(self, feedback_list, labels):
        """Organize feedback into cluster groups"""
        clusters = {}
        
        for idx, label in enumerate(labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(feedback_list[idx])
        
        return clusters
