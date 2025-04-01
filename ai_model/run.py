from src.collaborative_filtering import run_collaborative_filtering
from src.content_based_filtering import run_content_based_filtering
from src.clustering import run_clustering_analysis
from src.tfx_pipeline import run_pipeline
import os

def main():
    # Ensure output directories exist
    os.makedirs("outputs/models", exist_ok=True)
    os.makedirs("outputs/recommendations", exist_ok=True)
    
    print("Running Collaborative Filtering...")
    cf_model = run_collaborative_filtering()
    
    print("\nRunning Content-Based Filtering...")
    recommender = run_content_based_filtering()
    print("Sample recommendations for first hotel:", recommender("Hilton"))
    
    print("\nRunning Clustering Analysis...")
    clusters = run_clustering_analysis()
    print("User clusters summary:\n", clusters['user_clusters'].groupby('cluster').mean())
    
    print("\nRunning TFX Pipeline...")
    run_pipeline()

if __name__ == "__main__":
    main()