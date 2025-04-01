
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

from data_loader import load_trips
from surprise import Dataset, Reader, SVD
from surprise.model_selection import cross_validate

def run_collaborative_filtering():
    ratings_df = load_trips()
    
    # Filter to users with sufficient ratings
    user_counts = ratings_df['user_id'].value_counts()
    valid_users = user_counts[user_counts > 2].index
    ratings_df = ratings_df[ratings_df['user_id'].isin(valid_users)]
    
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(ratings_df, reader)
    
    algo = SVD()
    cv_results = cross_validate(algo, data, measures=['RMSE', 'MAE'], cv=3)
    print(f"Collaborative Filtering Performance: {cv_results}")
    
    # Train final model
    trainset = data.build_full_trainset()
    algo.fit(trainset)
    return algo