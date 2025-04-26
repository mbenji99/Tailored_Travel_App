import os
import joblib
import numpy as np
import pandas as pd

# Try/Try again to import TensorFlow or tflite_runtime
try:
    import tensorflow as tf
    _TF_AVAILABLE = True
except ImportError:
    _TF_AVAILABLE = False

# ——— Module-level caches ———
_cf_model       = None
_cb_recommender = None
_clusters       = None
_scaler         = None
_encoder        = None
_hybrid_model   = None
_feature_list   = None

def _load(path, loader, cache_name):
    global _cf_model, _cb_recommender, _clusters, _scaler, _encoder, _hybrid_model
    cache = globals()[cache_name]
    if cache is None:
        cache = loader(path)
        globals()[cache_name] = cache
    return cache

def _load_feature_list(path):
    global _feature_list
    if _feature_list is None:
        df = pd.read_csv(path)
        _feature_list = df['feature'].tolist()
    return _feature_list

def predict(
    user_id: str,
    item_id: str,
    *,
    model_path: str,
    scaler_path: str,
    encoder_path: str,
    cf_path: str,
    cb_path: str,
    cluster_path: str,
    feature_list_path: str = None,
    numeric_features: dict = None
) -> float:
    """
    Predict a rating for (user_id, item_id). If TF is unavailable,
    fall back to just the CF model’s estimate.
    """
    # ——— Load feature list (for the hybrid model) ———
    if feature_list_path is None:
        here = os.path.dirname(__file__)
        feature_list_path = os.path.abspath(os.path.join(here, '..', 'hybrid_feature_list.csv'))
    feature_list = _load_feature_list(feature_list_path)

    # ——— Load artifacts ———
    cf    = _load(cf_path,      joblib.load,               '_cf_model')
    try:
        cb    = _load(cb_path,      joblib.load,               '_cb_recommender')
    except:
        cb    = None
    try:
        cl    = _load(cluster_path, joblib.load,               '_clusters')
    except:
        cl    = None

    if _TF_AVAILABLE:
        scl   = _load(scaler_path,   joblib.load,               '_scaler')
        enc   = _load(encoder_path,  joblib.load,               '_encoder')
        model = _load(model_path,    tf.keras.models.load_model, '_hybrid_model')
    else:
        scl = enc = model = None

    # ——— Collaborative score ———
    try:
        cf_score = cf.predict(user_id, item_id).est
    except:
        cf_score = 0.0

    # ——— Content-based score ———
    if cb is not None:
        try:
            cb_score = float(cb(item_id).iloc[0]['cosine_similarity'])
        except:
            cb_score = 0.0
    else:
        cb_score = 0.0

    # If no hybrid model, just return CF
    if not _TF_AVAILABLE or model is None:
        return float(cf_score)

    # ——— Clusters (if present) ———
    if cl is not None:
        uc_df = cl.get('user_clusters', None)
        if uc_df is not None:
            mask = uc_df['user_id']==user_id
            user_cluster = int(uc_df.loc[mask,'cluster'].squeeze()) if mask.any() else -1
        else:
            user_cluster = -1
        dc_df = cl.get('destination_clusters', None)
        if dc_df is not None:
            col = 'Commodity' if 'Commodity' in dc_df.columns else dc_df.columns[0]
            mask = dc_df[col]==item_id
            dest_cluster = int(dc_df.loc[mask,'cluster'].squeeze()) if mask.any() else -1
        else:
            dest_cluster = -1
    else:
        user_cluster = dest_cluster = -1

    # ——— Numeric features ———
    n_num = scl.n_features_in_
    feat_names = feature_list[:n_num]
    orig = feat_names[:-2]  # drop CF,CB
    if numeric_features is None:
        numeric_features = {}
    vals = [float(numeric_features.get(name,0.0)) for name in orig] + [cf_score, cb_score]
    X_num = np.array(vals).reshape(1,-1)
    Xs = scl.transform(X_num)

    # ——— One-hot clusters ———
    cluster_vec = enc.transform([[user_cluster,dest_cluster]])

    # ——— Final & predict ———
    X = np.hstack([Xs, cluster_vec])
    pred = model.predict(X)
    return float(pred.squeeze())
