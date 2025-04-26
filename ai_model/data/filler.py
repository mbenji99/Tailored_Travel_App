import pandas as pd

# Load the dataset
df = pd.read_csv("Merged_Travel_Dataset.csv")

# Fill missing values smartly
for col in df.columns:
    if df[col].isnull().sum() > 0:
        if df[col].dtype == 'object':
            mode_val = df[col].mode()[0]
            df[col].fillna(mode_val, inplace=True)
            print(f"Filled missing in '{col}' with mode: {mode_val}")
        else:
            median_val = df[col].median()
            df[col].fillna(median_val, inplace=True)
            print(f"Filled missing in '{col}' with median: {median_val}")

# Save the filled version
df.to_csv("Filled_Merged_Travel_Dataset.csv", index=False)
print(" Missing values filled and saved as 'Filled_Merged_Travel_Dataset.csv'")
