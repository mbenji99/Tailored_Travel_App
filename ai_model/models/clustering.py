from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.mixture import GaussianMixture
import pandas as pd
from models.data_loader import load_trips, load_tourism_stats, load_user_profiles

class TravelClustering:
    def __init__(self, n_user_clusters=4, n_dest_clusters=5):
        self.n_user_clusters = n_user_clusters
        self.n_dest_clusters = n_dest_clusters
        self._cluster_users()
        self._cluster_destinations()
        
    def _cluster_users(self):
        """Cluster users based on travel patterns"""
        trips = load_trips()
        user_profiles = load_user_profiles()
        
        # User travel features
        travel_features = trips.groupby('user_id').agg({
            'rating': ['mean', 'count', 'std'],
            'item_id': 'nunique'
        })
        travel_features.columns = ['_'.join(col).strip() for col in travel_features.columns.values]
        
        # Merge with demographic data
        self.user_features = pd.merge(
            travel_features,
            user_profiles.set_index('user_id'),
            left_index=True,
            right_index=True,
            how='left'
        )
        
        # Select features for clustering
        cluster_features = self.user_features[[
            'rating_mean', 'rating_count', 'item_id_nunique',
            'age', 'income_level'
        ]].fillna(self.user_features.mean())
        
        # Standardize and cluster
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(cluster_features)
        
        self.user_cluster_model = GaussianMixture(n_components=self.n_user_clusters)
        self.user_features['cluster'] = self.user_cluster_model.fit_predict(scaled_features)
        
    def _cluster_destinations(self):
        """Cluster destinations based on tourism stats"""
        tourism = load_tourism_stats()
        
        # Select numeric features
        numeric_cols = tourism.select_dtypes(include=['float64', 'int64']).columns
        destination_features = tourism[numeric_cols].fillna(tourism[numeric_cols].mean())
        
        # Standardize and cluster
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(destination_features)
        
        self.dest_cluster_model = KMeans(n_clusters=self.n_dest_clusters)
        tourism['cluster'] = self.dest_cluster_model.fit_predict(scaled_features)
        self.destination_clusters = tourism[['Commodity', 'cluster']]
        
    def get_user_cluster(self, user_id):
        """Get cluster for a specific user"""
        return self.user_features.loc[user_id, 'cluster']
        
    def get_similar_users(self, user_id, n=5):
        """Get similar users in the same cluster"""
        cluster = self.get_user_cluster(user_id)
        same_cluster = self.user_features[self.user_features['cluster'] == cluster]
        return same_cluster.sample(min(n, len(same_cluster))).index.tolist()
        
    def get_cluster_destinations(self, cluster_id):
        """Get destinations in a specific cluster"""
        return self.destination_clusters[
            self.destination_clusters['cluster'] == cluster_id
        ]['Commodity'].tolist()