# ai_model/src/content_based_filtering.py

from data_loader import load_hotels
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pandas as pd

def run_content_based_filtering():
    # 1) Load
    hotels = load_hotels()

    # 2) Build a “description” column
    hotels['description'] = (
        hotels['name']
        + ' with '
        + hotels['num_rooms'].fillna(0).astype(int).astype(str)
        + ' rooms'
    )

    # 3) Fit TF-IDF
    vectorizer   = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(hotels['description'])

    # 4) Pre-compute similarity matrix
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    # 5) Index lookup
    name_to_idx = {name: idx for idx, name in enumerate(hotels['name'])}

    def get_recommendations(item_id: str, top_n: int = 3) -> pd.DataFrame:
        idx = name_to_idx.get(item_id)
        if idx is None:
            return pd.DataFrame(columns=hotels.columns)
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
        rec_idxs = [i for i, _ in sim_scores]
        return hotels.iloc[rec_idxs].copy()

    # **Return** all four pieces so the training script can dump them
    return vectorizer, tfidf_matrix, hotels, get_recommendations
