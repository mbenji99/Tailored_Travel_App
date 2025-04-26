
# This module implements a collaborative filtering recommendation system using the Surprise library.
# The module demonstrates the following:
# - Loading user-item rating data into a pandas DataFrame.
# - Converting the data into a Surprise-compatible format using the `Reader` and `Dataset` classes.
# - Applying the SVD (Singular Value Decomposition) algorithm for collaborative filtering.
# - Evaluating the model using cross-validation with RMSE and MAE metrics.
# - Training the model on the full dataset.
# - Making predictions for specific user-item pairs.

# Dependencies:
# - pandas
# - surprise

# Example usage:
#    Run the script to see cross-validation results and a sample prediction for a user-item pair.

from surprise import Dataset, Reader, SVD, accuracy
from surprise.model_selection import cross_validate, train_test_split
from sklearn.metrics import precision_score, recall_score
import pandas as pd
from models.data_loader import load_trips

def train_collaborative_filtering(min_ratings=3):
    ratings_df = load_trips()
    
    # Filter to active users
    user_counts = ratings_df['user_id'].value_counts()
    valid_users = user_counts[user_counts >= min_ratings].index
    ratings_df = ratings_df[ratings_df['user_id'].isin(valid_users)]
    
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(ratings_df, reader)
    
    algo = SVD(n_factors=50, n_epochs=20, lr_all=0.005, reg_all=0.02)
    
    # Cross-validation
    cv_results = cross_validate(algo, data, measures=['RMSE', 'MAE'], cv=5, verbose=True)
    
    # Additional metrics
    trainset, testset = train_test_split(data, test_size=0.2)
    algo.fit(trainset)
    predictions = algo.test(testset)
    
    # Convert to binary classification (like/dislike)
    binary_pred = [1 if pred.est >= 4 else 0 for pred in predictions]
    binary_true = [1 if pred.r_ui >= 4 else 0 for pred in predictions]
    
    metrics = {
        'rmse': accuracy.rmse(predictions),
        'mae': accuracy.mae(predictions),
        'precision': precision_score(binary_true, binary_pred),
        'recall': recall_score(binary_true, binary_pred)
    }
    
    # Final training on full dataset
    trainset = data.build_full_trainset()
    algo.fit(trainset)
    
    return algo, metrics

def predict_rating(model, user_id, item_id):
    return model.predict(user_id, item_id).est