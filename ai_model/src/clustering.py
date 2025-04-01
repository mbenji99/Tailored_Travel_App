
from data_loader import load_trips, load_tourism_stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd

def run_clustering_analysis():
    # User clustering based on trip patterns
    trips = load_trips()
    user_features = trips.groupby('user_id').agg({
        'rating': ['mean', 'count'],
        'item_id': 'nunique'
    }).droplevel(0, axis=1)
    
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(user_features)
    
    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(scaled_features)
    user_features['cluster'] = clusters
    
    # Destination clustering using tourism stats
    tourism = load_tourism_stats()
    destination_features = tourism.select_dtypes(include=['float64', 'int64'])
    destination_features = destination_features.fillna(destination_features.mean())
    
    destination_scaled = StandardScaler().fit_transform(destination_features)
    dest_clusters = KMeans(n_clusters=4).fit_predict(destination_scaled)
    
    return {
        'user_clusters': user_features,
        'destination_clusters': pd.DataFrame({
            'Commodity': tourism['Commodity'],
            'cluster': dest_clusters
        })
    }