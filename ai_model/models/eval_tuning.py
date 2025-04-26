#!/usr/bin/env python3
"""
eval_tuning.py

Step 1: Quantitative evaluation & basic hyper‑parameter tuning.
– Loads your pre‑scaled, merged dataset.
– Infers/validates rating, user_id, item_id.
– Computes collaborative‑filtering & content‑based scores.
– Assembles X,y (numeric + cf_score + cb_score).
– Splits into train/val/test.
– Trains a small NN, logs & plots train vs. val loss/MAE.
– Reports test MAE.
"""

import os, sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# allow imports of sibling modules in this folder
SCRIPT_DIR = os.path.dirname(__file__)
sys.path.insert(0, SCRIPT_DIR)

from collaborative_filtering import run_collaborative_filtering
from content_based_filtering import run_content_based_filtering

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras import Input, Model
from tensorflow.keras.layers import Dense, Dropout

# ————————————  
# 1  Load data
DATA_DIR  = os.path.abspath(os.path.join(SCRIPT_DIR, '..', 'data'))
DATA_FILE = os.path.join(DATA_DIR, 'Scaled_Merged_Travel_Dataset.csv')

print(f"Loading data from {DATA_FILE}…")
df = pd.read_csv(DATA_FILE, low_memory=False)

# ————————————  
# 2  Ensure we have a 'rating' column (or infer from cost/duration)
if 'rating' not in df.columns:
    if {'Total cost','Duration (days)'}.issubset(df.columns):
        df['rating'] = (df['Duration (days)'] 
                        / df['Duration (days)'].max() * 5).round(1)
    else:
        raise KeyError("No 'rating' column found and cannot infer it.")
df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0.0)

# ————————————  
# 3  Identify user_id & item_id
if 'user_id' not in df.columns:
    if 'Traveler name' in df.columns:
        df['user_id'] = df['Traveler name'].astype(str)
    else:
        raise KeyError("Cannot infer 'user_id'; add or rename a column to 'user_id'.")
if 'item_id' not in df.columns:
    if 'Destination' in df.columns:
        df['item_id'] = df['Destination'].astype(str)
    elif 'srch_destination_id' in df.columns:
        df['item_id'] = df['srch_destination_id'].astype(str)
    elif 'hotel_cluster' in df.columns:
        df['item_id'] = df['hotel_cluster'].astype(str)
    else:
        # fallback: first "*_encoded" containing "destination"
        enc = [c for c in df.columns if c.endswith('_encoded') and 'destination' in c]
        if enc:
            df['item_id'] = df[enc[0]].astype(str)
        else:
            raise KeyError("Cannot infer 'item_id'; ensure a destination field exists.")
df['user_id'] = df['user_id'].astype(str)
df['item_id'] = df['item_id'].astype(str)

# ————————————  
# 4  Collaborative‑Filtering scores
print("  Running Collaborative Filtering…")
cf_res = run_collaborative_filtering()
# CF module may return either just the algo or (pivot,algo)
cf_algo = cf_res[1] if isinstance(cf_res, tuple) else cf_res

def safe_cf(u,i):
    try:
        return cf_algo.predict(u,i).est
    except:
        return 0.0

df['cf_score'] = df.apply(lambda r: safe_cf(r['user_id'], r['item_id']), axis=1)

# ————————————  
# 5  Content‑Based similarity scores
print("  Running Content‑Based Filtering…")
cb = run_content_based_filtering()

def safe_cb(item):
    try:
        recs = cb(item)
        # assume your CB returns a df with 'cosine_similarity'
        return float(recs.iloc[0].get('cosine_similarity', 0.0))
    except:
        return 0.0

df['cb_score'] = df['item_id'].apply(safe_cb)

# ————————————  
# 6  Assemble feature matrix X and target y
# pick only numeric features
numeric_cols = (
    df.select_dtypes(include=['int64','float64'])
      .columns
      .difference(['rating'])
      .tolist()
)
feature_cols = numeric_cols + ['cf_score','cb_score']

print("Features:", feature_cols)
X = df[feature_cols].values
y = df['rating'].values

# ————————————  
# 7  Train / Val / Test split (60/20/20)
X_temp, X_test,  y_temp, y_test  = train_test_split(X, y, test_size=0.2, random_state=42)
X_train, X_val,  y_train, y_val  = train_test_split(X_temp, y_temp,
                                                   test_size=0.25, # .25 x .8 = .2
                                                   random_state=42)

  
# 8  Scale numeric portion only
n_num = len(numeric_cols)
scaler = StandardScaler()
X_train[:, :n_num] = scaler.fit_transform(X_train[:, :n_num])
X_val[:,   :n_num] = scaler.transform(X_val[:,   :n_num])
X_test[:,  :n_num] = scaler.transform(X_test[:,  :n_num])

  
# 9  Model factory
def build_model(input_dim,
                hidden_units=[128,64],
                lr=1e-3,
                dropout=0.3):
    inp = Input(shape=(input_dim,))
    x   = inp
    for u in hidden_units:
        x = Dense(u, activation='relu')(x)
        x = Dropout(dropout)(x)
    out = Dense(1)(x)
    m   = Model(inp,out)
    m.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=lr),
              loss='mse', metrics=['mae'])
    return m

 
# 10 Train & validate
model = build_model(input_dim=X_train.shape[1])
history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=20,
    batch_size=32,
    verbose=1
)

 
#  Plot loss & MAE
plt.figure(figsize=(12,5))

plt.subplot(1,2,1)
plt.plot(history.history['loss'], label='train_loss')
plt.plot(history.history['val_loss'], label='val_loss')
plt.title('MSE Loss'); plt.legend()

plt.subplot(1,2,2)
plt.plot(history.history['mae'], label='train_mae')
plt.plot(history.history['val_mae'], label='val_mae')
plt.title('MAE'); plt.legend()

plt.tight_layout()
plt.show()

# ————————————  
# ⓫  Final test evaluation
test_loss, test_mae = model.evaluate(X_test, y_test, verbose=0)
print(f"\n  Final Test MAE: {test_mae:.4f}")
