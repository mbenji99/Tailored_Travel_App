from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
import pandas as pd
from models.data_loader import load_hotels, load_destinations

class ContentBasedRecommender:
    def __init__(self):
        self.hotels = load_hotels()
        self.destinations = load_destinations()
        self._prepare_data()
        self._train_model()
        
    def _prepare_data(self):
        """Merge and prepare data for content-based recommendations"""
        self.merged = pd.merge(
            self.hotels,
            self.destinations,
            left_on='NAME',
            right_on='srch_destination_id',
            how='left'
        )
        
        # Create rich description
        self.merged['description'] = (
            self.merged['NAME'] + " in " + 
            self.merged['hotel_country'] + " | " +
            "Stars: " + self.merged['STARS'].astype(str) + " | " +
            "Rooms: " + self.merged['NUMROOMS'].astype(str) + " | " +
            "Popularity: " + self.merged['popularity'].astype(str)
        )
        
    def _train_model(self):
        """Train TF-IDF and similarity matrices"""
        self.tfidf = TfidfVectorizer(stop_words='english', max_features=5000)
        self.tfidf_matrix = self.tfidf.fit_transform(self.merged['description'])
        self.cosine_sim = linear_kernel(self.tfidf_matrix, self.tfidf_matrix)
        
        # Additional similarity matrix for numeric features
        numeric_features = self.merged[['STARS', 'NUMROOMS', 'popularity', 'avg_rating']]
        self.numeric_sim = cosine_similarity(numeric_features)
        
    def recommend(self, hotel_name, n=5, realtime_factors=None):
        """Get recommendations for a hotel/destination"""
        try:
            idx = self.merged.index[self.merged['NAME'] == hotel_name].tolist()[0]
        except IndexError:
            return pd.DataFrame()  # Return empty if not found
            
        # Combine content and numeric similarities
        combined_sim = 0.6 * self.cosine_sim[idx] + 0.4 * self.numeric_sim[idx]
        
        # Apply real-time factors if provided
        if realtime_factors:
            combined_sim = self._apply_realtime_factors(combined_sim, realtime_factors)
            
        sim_scores = list(enumerate(combined_sim))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:n+1]
        
        return self.merged.iloc[[i[0] for i in sim_scores]]
    
    def _apply_realtime_factors(self, similarity_scores, factors):
        """Adjust scores based on real-time factors"""
        # Example adjustment - can be customized
        if factors.get('weather') == 'rainy':
            similarity_scores *= 0.9  # Slightly reduce scores in bad weather
        if factors.get('price_change') > 0.1:  # More than 10% price increase
            similarity_scores *= 0.8
        return similarity_scores