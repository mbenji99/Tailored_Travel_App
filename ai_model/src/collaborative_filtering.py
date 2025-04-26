
import numpy as np
from data_loader import load_trips
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import LabelEncoder

def run_collaborative_filtering(n_components=20):
    """
    Returns:
      - predict(user_id, item_id) -> float score
      - encoders and factor matrices, in case you need them downstream
    """
    df = load_trips()  # must have ['user_id','item_id','rating']

    # 1 Label‑encode users & items to indices
    user_enc = LabelEncoder().fit(df['user_id'])
    item_enc = LabelEncoder().fit(df['item_id'])
    df['u_idx'] = user_enc.transform(df['user_id'])
    df['i_idx'] = item_enc.transform(df['item_id'])

    n_users = df['u_idx'].nunique()
    n_items = df['i_idx'].nunique()

    # 2 Build user×item rating matrix (fill missing with zeros)
    mat = np.zeros((n_users, n_items), dtype=float)
    for _, row in df.iterrows():
        mat[row['u_idx'], row['i_idx']] = row['rating']

    # 3 Truncated SVD
    svd = TruncatedSVD(n_components=n_components, random_state=42)
    user_factors = svd.fit_transform(mat)            # shape (n_users,  n_comp)
    item_factors = svd.components_.T               # shape (n_items,  n_comp)

    # 4 A simple predict(u,i) = dot(user_factors[u], item_factors[i])
    def predict(user_id, item_id):
        try:
            u = user_enc.transform([user_id])[0]
            i = item_enc.transform([item_id])[0]
            return float(np.dot(user_factors[u], item_factors[i]))
        except Exception:
            return 0.0

    return predict, user_enc, item_enc, user_factors, item_factors
