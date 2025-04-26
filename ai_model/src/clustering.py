# ai_model/src/clustering.py

import pandas as pd
from data_loader import load_trips, load_tourism_stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def run_clustering_analysis():
    # —————————————————————————————————————————————
    # 1) User clustering based on trip patterns
    trips = load_trips()  # expects ['user_id','item_id','rating']
    # aggregate per user
    user_features = (
        trips
        .groupby('user_id')
        .agg(
            rating_mean=('rating','mean'),
            rating_count=('rating','count'),
            dest_count=('item_id','nunique')
        )
        .reset_index()
    )
    # scale
    scaler = StandardScaler()
    scaled_users = scaler.fit_transform(user_features[['rating_mean','rating_count','dest_count']])
    # cluster
    k_u = KMeans(n_clusters=3, random_state=42)
    user_clusters = k_u.fit_predict(scaled_users)
    user_features['cluster'] = user_clusters

    # —————————————————————————————————————————————
    # 2) Destination clustering from tourism/economic stats
    tourism = load_tourism_stats()  # your Standardized_TourSat2023.csv
    # choose the id column—here I'm assuming it's called "Category"
    if 'Category' in tourism.columns:
        id_col = 'Category'
    elif 'Sector' in tourism.columns:
        id_col = 'Sector'
    else:
        raise KeyError("Couldn't find a destination ID column in tourism stats")

    # numeric features only
    num_cols = tourism.select_dtypes(include=['int64','float64']).columns
    tourism_num = tourism[num_cols].fillna(tourism[num_cols].mean())

    # scale + cluster
    scaled_dest = StandardScaler().fit_transform(tourism_num)
    k_d = KMeans(n_clusters=4, random_state=42)
    dest_clusters = k_d.fit_predict(scaled_dest)

    destination_clusters = pd.DataFrame({
        'item_id': tourism[id_col].astype(str),
        'dest_cluster': dest_clusters
    })

    return {
        'user_clusters': user_features[['user_id','cluster']],
        'destination_clusters': destination_clusters
    }
