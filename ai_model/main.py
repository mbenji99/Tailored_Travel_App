from models.hybrid_recommender import HybridRecommender
import pandas as pd
import time

def main():
    # Initialize the recommender system
    print("Starting TailoredTravel Recommendation System...")
    start_time = time.time()
    recommender = HybridRecommender()
    init_time = time.time() - start_time
    print(f"System initialized in {init_time:.2f} seconds\n")
    
    # Example usage
    while True:
        print("\n1. Get personalized recommendations")
        print("2. Get similar destination recommendations")
        print("3. Get cold start recommendations")
        print("4. Exit")
        choice = input("Enter your choice: ")
        
        if choice == '1':
            user_id = input("Enter user ID: ")
            n = int(input("Number of recommendations: "))
            weather = input("Current weather (sunny/rainy/etc): ")
            
            recs = recommender.recommend(
                user_id=user_id,
                n=n,
                realtime_factors={'weather': weather}
            )
            print("\nTop Recommendations:")
            print(recs.to_string(index=False))
            
        elif choice == '2':
            user_id = input("Enter user ID: ")
            destination = input("Enter destination you like: ")
            n = int(input("Number of recommendations: "))
            
            recs = recommender.recommend(
                user_id=user_id,
                destination=destination,
                n=n
            )
            print("\nSimilar Destinations:")
            print(recs[['NAME', 'hotel_country', 'STARS']].to_string(index=False))
            
        elif choice == '3':
            n = int(input("Number of recommendations: "))
            season = input("Current season: ")
            
            recs = recommender.recommend(
                user_id=None,
                n=n,
                realtime_factors={'season': season}
            )
            print("\nPopular Recommendations:")
            print(recs.to_string(index=False))
            
        elif choice == '4':
            print("Exiting...")
            break
            
        else:
            print("Invalid choice, please try again")

if __name__ == "__main__":
    main()