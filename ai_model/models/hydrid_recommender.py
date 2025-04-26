from models.collaborative_filtering import train_collaborative_filtering, predict_rating
from models.content_based_filtering import ContentBasedRecommender
from models.clustering import TravelClustering
from models.data_loader import load_trips
import pandas as pd
import numpy as np

class HybridRecommender:
    def __init__(self):
        print("Initializing recommendation models...")
        self.cf_model, self.cf_metrics = train_collaborative_filtering()
        self.cb_recommender = ContentBasedRecommender()
        self.clustering = TravelClustering()
        self.ratings_data = load_trips()
        print("All models initialized successfully!")
        
    def recommend(self, user_id=None, destination=None, n=5, realtime_factors=None):
        """
        Get hybrid recommendations for a user
        Args:
            user_id: User ID (None for cold start)
            destination: Specific destination to get similar items (optional)
            n: Number of recommendations
            realtime_factors: Dictionary of real-time factors
        """
        if user_id is None:
            return self._cold_start_recommendations(n, realtime_factors)
            
        if destination:
            return self._similar_items_recommendation(user_id, destination, n, realtime_factors)
        else:
            return self._personalized_recommendations(user_id, n, realtime_factors)
    
    def _personalized_recommendations(self, user_id, n, realtime_factors):
        """Generate personalized recommendations"""
        # Get collaborative filtering predictions
        all_destinations = self.ratings_data['item_id'].unique()
        cf_predictions = []
        for dest in all_destinations:
            cf_predictions.append({
                'destination': dest,
                'cf_score': predict_rating(self.cf_model, user_id, dest)
            })
        cf_predictions = pd.DataFrame(cf_predictions)
        
        # Get cluster-based recommendations
        user_cluster = self.clustering.get_user_cluster(user_id)
        cluster_dests = self.clustering.get_cluster_destinations(user_cluster)
        
        # Combine recommendations
        recommendations = cf_predictions
        recommendations['cluster_boost'] = recommendations['destination'].isin(cluster_dests) * 0.5
        recommendations['final_score'] = recommendations['cf_score'] + recommendations['cluster_boost']
        
        # Apply real-time factors
        if realtime_factors:
            recommendations = self._apply_realtime_factors(recommendations, realtime_factors)
            
        return recommendations.sort_values('final_score', ascending=False).head(n)
    
    def _similar_items_recommendation(self, user_id, destination, n, realtime_factors):
        """Get recommendations similar to a specific destination"""
        # Content-based recommendations
        cb_recs = self.cb_recommender.recommend(destination, n*2, realtime_factors)
        if cb_recs.empty:
            return pd.DataFrame()
            
        # Add collaborative filtering scores
        cb_recs['cf_score'] = cb_recs['NAME'].apply(
            lambda x: predict_rating(self.cf_model, user_id, x))
            
        # Add cluster boost
        user_cluster = self.clustering.get_user_cluster(user_id)
        cb_recs['cluster_boost'] = cb_recs['srch_destination_id'].apply(
            lambda x: 0.5 if x in self.clustering.get_cluster_destinations(user_cluster) else 0)
            
        cb_recs['final_score'] = cb_recs['cf_score'] + cb_recs['cluster_boost']
        
        return cb_recs.sort_values('final_score', ascending=False).head(n)
    
    def _cold_start_recommendations(self, n, realtime_factors):
        """Recommendations for new users"""
        # Get popular items in the most common cluster
        common_cluster = self.clustering.user_features['cluster'].mode()[0]
        cluster_dests = self.clustering.get_cluster_destinations(common_cluster)
        
        # Get highest rated items in this cluster
        popular_items = self.ratings_data[
            self.ratings_data['item_id'].isin(cluster_dests)
        ].groupby('item_id')['rating'].mean().sort_values(ascending=False).head(n*2)
        
        # Apply content-based filtering to enhance
        recs = []
        for dest in popular_items.index:
            similar = self.cb_recommender.recommend(dest, 1, realtime_factors)
            if not similar.empty:
                recs.append({
                    'destination': dest,
                    'similar_to': similar['NAME'].values[0],
                    'score': popular_items[dest]
                })
        
        return pd.DataFrame(recs).sort_values('score', ascending=False).head(n)
    
    def _apply_realtime_factors(self, recommendations, factors):
        """Adjust recommendations based on real-time factors"""
        # Example adjustments - can be customized
        if factors.get('weather') == 'rainy':
            recommendations['final_score'] *= 0.9
        if factors.get('high_season', False):
            recommendations['final_score'] *= 1.1
        return recommendations
    
    def recommend_for_new_user(self, demographic_data):
        # Use content-based and cluster-based approaches only
        similar_users = self._find_similar_demographic_users(demographic_data)
        return self._get_popular_in_cluster(similar_users)