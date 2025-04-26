# standardize_dataset.py
import pandas as pd
from sklearn.preprocessing import StandardScaler

# Replace this with the actual engineered dataset file
input_file = "Engineered_TravelerTripDataset.csv"
output_file = "Standardized_TravelerTripDataset.csv"

# Load the dataset
df = pd.read_csv(input_file)

# Identify only numeric columns for standardization
numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns

# Standardize
scaler = StandardScaler()
df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

# Save the standardized version
df.to_csv(output_file, index=False)
print(f"{output_file} created successfully.")
