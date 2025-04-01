
from data_loader import load_hotels, load_destinations
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pandas as pd

def run_content_based_filtering():
    hotels = load_hotels()
    destinations = load_destinations()
    
    # Merge hotel data with destination info
    merged = pd.merge(
        hotels,
        destinations,
        left_on='NAME',
        right_on='srch_destination_id',
        how='left'
    )
    
    # Create composite description
    merged['description'] = (
        merged['NAME'] + " in " + 
        merged['hotel_country'] + " with " + 
        merged['NUMROOMS'].astype(str) + " rooms"
    )
    
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(merged['description'])
    
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    
    # Recommendation function
    def get_recommendations(hotel_name, cosine_sim=cosine_sim):
        idx = merged.index[merged['NAME'] == hotel_name].tolist()[0]
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:4]
        return merged.iloc[[i[0] for i in sim_scores]]
    
    return get_recommendations