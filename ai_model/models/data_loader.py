import pandas as pd
import numpy as np
from ai_model.configs.data_config import DATA_PATHS

def load_trips():
    """Load trip details with ratings inferred from duration/cost"""
    df = pd.read_csv(DATA_PATHS['trips'])
    
    # Create synthetic ratings based on trip characteristics
    df['normalized_duration'] = df['Duration (days)'] / df['Duration (days)'].max()
    df['normalized_cost'] = 1 - (df['Cost'] / df['Cost'].max()) # Lower cost = higher rating
    df['season_factor'] = np.where(
        df['Season'].isin(['Summer', 'Winter']), 1.2, 1.0)  
    
    df['rating'] = (
            (0.5 * df['normalized_duration'] + 
            0.3 * df['normalized_cost'] + 
            0.2 * df['season_factor']) * 4 + 1
            ).clip(1, 5).round(1) # Scale to 1-5 range
    
    return df[['Traveler name', 'Destination', 'rating']].rename(columns={
        'Traveler name': 'user_id',
        'Destination': 'item_id'
    })

def load_destinations():
    """Load destination data with additional features"""
    df = pd.read_csv(DATA_PATHS['travel_activity'])
    return df.groupby('srch_destination_id').first().reset_index()[
        ['srch_destination_id', 'hotel_country', 'popularity', 'avg_rating']
    ]

def load_tourism_stats():
    """Load tourism economic data with preprocessing"""
    df = pd.read_excel(DATA_PATHS['tourism_stats'])
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
    return df

def load_hotels():
    """Load hotel data with enhanced features"""
    hotels = pd.read_csv(DATA_PATHS['hotels'])
    return hotels[['NAME', 'ADDRESS', 'NUMROOMS', 'X', 'Y', 'STARS']].rename(columns={
        'X': 'longitude',
        'Y': 'latitude'
    })

def load_user_profiles():
    """Load user profiles for cold start problem"""
    return pd.read_csv(DATA_PATHS['user_profiles'])