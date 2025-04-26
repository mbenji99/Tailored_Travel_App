#!/usr/bin/env python3
"""
Hybrid Travel Recommender Training Script
"""
import os, sys, csv
from datetime import datetime
import pandas as pd, numpy as np

# allow imports of sibling modules
SCRIPT_DIR = os.path.dirname(__file__)
sys.path.insert(0, SCRIPT_DIR)

from collaborative_filtering import run_collaborative_filtering
from content_based_filtering import run_content_based_filtering
from clustering import run_clustering_analysis

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder

# TensorFlow imports
import tensorflow as tf
from tensorflow.keras import Input, Model
from tensorflow.keras.layers import Dense, Dropout

import joblib

# ── Paths & Hyperparameters ───────────────────────────────────────────────────

DATA_PATH       = os.path.abspath(os.path.join(SCRIPT_DIR, '..', 'data',
                        'Scaled_Merged_Travel_Dataset_augmented.csv'))
MODEL_DIR       = os.path.abspath(os.path.join(SCRIPT_DIR, '..', 'outputs','models'))
os.makedirs(MODEL_DIR, exist_ok=True)

KERAS_MODEL_PATH  = os.path.join(MODEL_DIR, 'hybrid_travel_recommender_model.keras')
SCALER_PATH       = os.path.join(MODEL_DIR, 'scaler.joblib')
ENCODER_PATH      = os.path.join(MODEL_DIR, 'encoder.joblib')
CF_PATH           = os.path.join(MODEL_DIR, 'cf_model.joblib')
CB_PATH           = os.path.join(MODEL_DIR, 'cb_recommender.joblib')
CLUSTER_PATH      = os.path.join(MODEL_DIR, 'clusters.joblib')
FEATURE_LIST_PATH = os.path.join(MODEL_DIR, 'hybrid_feature_list.csv')
LOG_PATH          = os.path.abspath(os.path.join(SCRIPT_DIR, '..', 'training_logs.csv'))

HP_UNITS   = 96
HP_DROPOUT = False
HP_LR      = 0.008820419054473111


def train_and_save():
    # ── 1) Load & prepare rating ────────────────────────────────────────────────
    df = pd.read_csv(DATA_PATH, low_memory=False)

    if 'rating' not in df:
        if {'Total cost','Duration (days)'}.issubset(df.columns):
            df['rating'] = (
                df['Duration (days)'] / df['Duration (days)'].max() * 5
            ).round(1)
        else:
            raise KeyError("No 'rating' column to train on.")
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0.0)

    # ── 2) user_id & item_id inference ─────────────────────────────────────────
    if 'user_id' not in df:
        if 'Traveler name' in df:
            df['user_id'] = df['Traveler name'].astype(str)
        else:
            raise KeyError("Cannot infer 'user_id'.")

    df['user_id'] = df['user_id'].astype(str)

    if 'item_id' not in df:
        for col in ['location','Destination','srch_destination_id','hotel_cluster']:
            if col in df:
                df['item_id'] = df[col].astype(str)
                break
        else:
            raise KeyError("Cannot infer 'item_id'.")
    df['item_id'] = df['item_id'].astype(str)

    # ── 3) Collaborative Filtering ───────────────────────────────────────────────
    print("Running Collaborative Filtering…")
    cf_predict_fn, user_enc, item_enc, user_factors, item_factors = run_collaborative_filtering()
    # apply CF score back into DataFrame for hybrid features
    df['cf_score'] = df.apply(lambda r: cf_predict_fn(r['user_id'], r['item_id']), axis=1)

    # ── 4) Content-Based Filtering ──────────────────────────────────────────────
    print("Running Content-Based Filtering…")
    vectorizer, tfidf_matrix, hotels_df, cb_recs_fn = run_content_based_filtering()

    def get_cb_score(item_id):
        recs = cb_recs_fn(item_id, top_n=1)
        if recs.empty or 'cosine_similarity' not in recs:
            return 0.0
        return float(recs.iloc[0].get('cosine_similarity', 0.0))

    df['cb_score'] = df['item_id'].apply(get_cb_score)

    # ── 5) Clustering ───────────────────────────────────────────────────────────
    print("Running Clustering Analysis…")
    clusters = run_clustering_analysis()
    user_clusters = clusters['user_clusters'].rename(columns={'cluster':'user_cluster'})
    dest_clusters = clusters['destination_clusters'].rename(columns={'dest_cluster':'dest_cluster'})

    df = df.merge(user_clusters, on='user_id', how='left')
    df = df.merge(dest_clusters, on='item_id', how='left')
    df['user_cluster'] = df['user_cluster'].fillna(-1).astype(int)
    df['dest_cluster'] = df['dest_cluster'].fillna(-1).astype(int)

    # ── 6) Build hybrid feature matrix ──────────────────────────────────────────
    numeric_cols = df.select_dtypes(include=['int64','float64']).columns.difference(['rating']).tolist()
    feature_cols = numeric_cols + ['cf_score','cb_score']

    encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    cluster_mat = encoder.fit_transform(df[['user_cluster','dest_cluster']])
    cluster_names = encoder.get_feature_names_out(['user_cluster','dest_cluster'])

    X_num = df[feature_cols].values
    X     = np.hstack([X_num, cluster_mat])
    y     = df['rating'].values

    # ── 7) Split & scale ─────────────────────────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    scaler = StandardScaler()
    n_num  = len(feature_cols)
    X_train[:, :n_num] = scaler.fit_transform(X_train[:, :n_num])
    X_test[:, :n_num]  = scaler.transform(X_test[:, :n_num])

    # ── 8) Build, compile & train model ─────────────────────────────────────────
    inp = Input(shape=(X_train.shape[1],), name='features')
    x   = Dense(HP_UNITS, activation='relu')(inp)
    if HP_DROPOUT:
        x = Dropout(0.2)(x)
    out = Dense(1, name='rating')(x)

    model = Model(inputs=inp, outputs=out)
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=HP_LR),
                  loss='mse', metrics=['mse','mae'])
    model.fit(X_train, y_train,
              validation_data=(X_test, y_test),
              epochs=15, batch_size=32, verbose=2)

    loss, mse, mae = model.evaluate(X_test, y_test, verbose=0)
    print(f"Test MSE: {mse:.4f}, MAE: {mae:.4f}")

    # ── 9) Log metrics ───────────────────────────────────────────────────────────
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, 'w', newline='') as f:
            csv.writer(f).writerow(['timestamp','model_file','train_size','test_size','mse','mae'])
    with open(LOG_PATH, 'a', newline='') as f:
        csv.writer(f).writerow([
            datetime.utcnow().isoformat(),
            KERAS_MODEL_PATH,
            len(X_train),
            len(X_test),
            float(mse),
            float(mae)
        ])

    # ── 10) Save all artifacts ───────────────────────────────────────────────────
    model.save(KERAS_MODEL_PATH)
    pd.DataFrame({'feature': feature_cols + list(cluster_names)})\
      .to_csv(FEATURE_LIST_PATH, index=False)

    joblib.dump(scaler,     SCALER_PATH)
    joblib.dump(encoder,    ENCODER_PATH)

    # **Collaborative**: dump the *data* needed, not the nested fn
    joblib.dump({
        'user_enc':     user_enc,
        'item_enc':     item_enc,
        'user_factors': user_factors,
        'item_factors': item_factors
    }, CF_PATH)

    # **Content-Based**: dump the TF-IDF pieces
    joblib.dump({
        'vectorizer':   vectorizer,
        'tfidf_matrix': tfidf_matrix,
        'hotels_df':    hotels_df
    }, CB_PATH)

    # **Clustering**: dump the two DataFrames
    joblib.dump(clusters, CLUSTER_PATH)

    # ── 11) (optional) export TFLite ───────────────────────────────────────────
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    tflite_model = converter.convert()
    with open(KERAS_MODEL_PATH.replace('.keras','.tflite'), 'wb') as f:
        f.write(tflite_model)

    print("All artifacts saved to", MODEL_DIR)


if __name__ == '__main__':
    train_and_save()
