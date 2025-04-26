import pandas as pd

# Load datasets
traveler_df = pd.read_csv("Standardized_TravelerTripDataset.csv")
expedia_df = pd.read_csv("Standardized_ExpediaDataset.csv")
hotels_df = pd.read_csv("Standardized_Hotels.csv")
travel_df = pd.read_csv("Standardized_Travel.csv")
toursat_df = pd.read_csv("Standardized_TourSat2023.csv")

# Print initial column names to debug
print("Traveler columns:", traveler_df.columns)
print("Expedia columns:", expedia_df.columns)
print("Hotels columns:", hotels_df.columns)
print("Travel columns:", travel_df.columns)
print("TourSat columns:", toursat_df.columns)

# Rename to unify join key for merging on 'location'
if "Destination" in traveler_df.columns:
    traveler_df.rename(columns={"Destination": "location"}, inplace=True)

if "srch_destination_id" in expedia_df.columns:
    expedia_df.rename(columns={"srch_destination_id": "location"}, inplace=True)

if "Destination" in travel_df.columns:
    travel_df.rename(columns={"Destination": "location"}, inplace=True)

if "Zipcode" in hotels_df.columns:
    hotels_df.rename(columns={"Zipcode": "location"}, inplace=True)

if "Industry" in toursat_df.columns:
    toursat_df.rename(columns={"Industry": "location"}, inplace=True)

# Convert location columns to string if they exist
for df in [traveler_df, expedia_df, travel_df, hotels_df, toursat_df]:
    if "location" in df.columns:
        df["location"] = df["location"].astype(str)

# Merge datasets step by step (only if 'location' is present)
merged_df = traveler_df
if "location" in expedia_df.columns:
    merged_df = pd.merge(merged_df, expedia_df, how='outer', on='location')
if "location" in hotels_df.columns:
    merged_df = pd.merge(merged_df, hotels_df, how='left', on='location')
if "location" in travel_df.columns:
    merged_df = pd.merge(merged_df, travel_df, how='left', on='location')
if "location" in toursat_df.columns:
    merged_df = pd.merge(merged_df, toursat_df, how='left', on='location')

# Save final dataset
merged_df.to_csv("Merged_Travel_Dataset.csv", index=False)
print("✅ Merged dataset saved as 'Merged_Travel_Dataset.csv'")
