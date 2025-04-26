#!/usr/bin/env python3
"""
hyperparam_tuning.py

Performs hyperparameter tuning on our hybrid travel recommender:
- Loads the merged, pre‑scaled dataset
- Infers/validates user_id, item_id, rating
- Extracts collaborative, content-based, clustering features
- Sets up a Keras Tuner search over a simple MLP
"""

import os
import sys
import pandas as pd
import numpy as np

# allow imports of our modules in ai_model/src
SCRIPT_DIR = os.path.dirname(__file__)
sys.path.insert(0, SCRIPT_DIR)

from collaborative_filtering import run_collaborative_filtering
from content_based_filtering import run_content_based_filtering
from clustering import run_clustering_analysis

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import keras_tuner as kt
import tensorflow as tf
from tensorflow.keras import Input, Model
from tensorflow.keras.layers import Dense, Dropout

# ————————————
# 1️⃣ Load pre‑scaled, merged data
DATA_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, '..', 'data', 'Scaled_Merged_Travel_Dataset_augmented.csv'))
df = pd.read_csv(DATA_PATH, low_memory=False)

# ————————————
# 2️⃣ Ensure rating exists (or infer)
if 'rating' not in df.columns:
    if {'Total cost', 'Duration (days)'}.issubset(df.columns):
        df['rating'] = (df['Duration (days)'] / df['Duration (days)'].max() * 5).round(1)
    else:
        raise KeyError("No 'rating' column and cannot infer it.")
df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0.0)

# ————————————
# 3️⃣ Infer user_id & item_id
if 'user_id' not in df.columns:
    if 'Traveler name' in df.columns:
        df['user_id'] = df['Traveler name'].astype(str)
    else:
        raise KeyError("Cannot infer 'user_id'.")
if 'item_id' not in df.columns:
    if 'Destination' in df.columns:
        df['item_id'] = df['Destination'].astype(str)
    elif 'srch_destination_id' in df.columns:
        df['item_id'] = df['srch_destination_id'].astype(str)
    elif 'hotel_cluster' in df.columns:
        df['item_id'] = df['hotel_cluster'].astype(str)
    else:
        # fallback: first *_encoded with 'destination'
        enc = [c for c in df.columns if c.endswith('_encoded') and 'destination' in c]
        if enc:
            df['item_id'] = df[enc[0]].astype(str)
        else:
            raise KeyError("Cannot infer 'item_id'.")
df['user_id'] = df['user_id'].astype(str)
df['item_id'] = df['item_id'].astype(str)

# ————————————
# 4️⃣ Collaborative filtering scores
print("▶️ Running Collaborative Filtering…")
cf_res = run_collaborative_filtering()
# handle both return styles
if isinstance(cf_res, tuple) and len(cf_res) == 2:
    _, cf_algo = cf_res
else:
    cf_algo = cf_res

def get_cf_score(u, i):
    try:
        return cf_algo.predict(u, i).est
    except:
        return 0.0

df['cf_score'] = df.apply(lambda r: get_cf_score(r['user_id'], r['item_id']), axis=1)

# ————————————
# 5️⃣ Content‑based similarity
print("▶️ Running Content‑Based Filtering…")
cb_recommender = run_content_based_filtering()

def get_cb_score(item):
    try:
        recs = cb_recommender(item)
        return float(recs.iloc[0].get('cosine_similarity', 0.0))
    except:
        return 0.0

df['cb_score'] = df['item_id'].apply(get_cb_score)

# ————————————
# 6️⃣ Clustering features
print("▶️ Running Clustering Analysis…")
clusters = run_clustering_analysis()

# user clusters: reset_index to get user_id column
uc = (
    clusters['user_clusters']
      .reset_index()[['user_id','cluster']]
      .rename(columns={'cluster':'user_cluster'})
)

# destination clusters: rename Commodity→item_id
dc = (
    clusters['destination_clusters']
      .rename(columns={'cluster':'dest_cluster','Commodity':'item_id'})
)

# merge into df
df = df.merge(uc, on='user_id', how='left')
df = df.merge(dc[['item_id','dest_cluster']], on='item_id', how='left')
df['dest_cluster'] = df['dest_cluster'].fillna(-1)

# ————————————
# 7️⃣ Assemble features + target
numeric_cols = df.select_dtypes(include=['int64','float64'])\
                 .columns.difference(['rating']).tolist()
feature_cols = numeric_cols + ['cf_score','cb_score']

encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
cluster_matrix = encoder.fit_transform(df[['user_cluster','dest_cluster']].fillna(-1))
cluster_features = encoder.get_feature_names_out(['user_cluster','dest_cluster'])

X_num = df[feature_cols].values
X = np.hstack([X_num, cluster_matrix])
y = df['rating'].values

# ————————————
# 8️⃣ Train/Test split & scaling
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler = StandardScaler()
n_num = len(feature_cols)
X_train[:, :n_num] = scaler.fit_transform(X_train[:, :n_num])
X_test[:, :n_num]  = scaler.transform(X_test[:, :n_num])

# ————————————
# instantiate the hyper‑parameters object
hp = kt.HyperParameters()
# 9️⃣ Define model builder for Keras Tuner
def build_model(hp):
    inp = Input(shape=(X_train.shape[1],))
    x = inp
    # tune number of layers and units
    for i in range(hp.Int('n_layers', 1, 3)):
        units = hp.Int(f'units_{i}', min_value=32, max_value=256, step=32)
        x = Dense(units, activation='relu')(x)
        if hp.Boolean(f'dropout_{i}'):
            rate = hp.Float(f'drop_rate_{i}', 0.1, 0.5, step=0.1)
            x = Dropout(rate)(x)
    out = Dense(1)(x)
    model = Model(inp, out)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(
            learning_rate=hp.Float('lr', 1e-4, 1e-2, sampling='log')
        ),
        loss='mse',
        metrics=['mae']
    )
    return model

tuner = kt.RandomSearch(
    build_model,
    objective='val_mae',
    max_trials=10,
    executions_per_trial=1,
    directory='hyperparam_logs',
    project_name='tailored_travels'
)

tuner.search(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=5,
    batch_size=hp.Choice('batch_size', [32, 64, 128])
)

# ————————————
# ⓪ Report best hyperparameters
best = tuner.get_best_hyperparameters(num_trials=1)[0]
print("Best hyperparameters:")
for key in best.values:
    print(f"  {key}: {best.get(key)}")
