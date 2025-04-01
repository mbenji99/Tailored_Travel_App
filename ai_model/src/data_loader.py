import pandas as pd
from data_config import DATA_PATHS

def load_trips():
    """Load trip details with ratings inferred from duration/cost"""
    df = pd.read_csv(DATA_PATHS['trips'])
    
    # Create synthetic ratings based on trip characteristics
    df['rating'] = (df['Duration (days)'] / df['Duration (days)'].max() * 5).round(1)
    return df[['Traveler name', 'Destination', 'rating']].rename(columns={
        'Traveler name': 'user_id',
        'Destination': 'item_id'
    })

def load_destinations():
    """Load destination data from travel activity logs"""
    df = pd.read_csv(DATA_PATHS['travel_activity'])
    return df.groupby('srch_destination_id').first().reset_index()[['srch_destination_id', 'hotel_country']]

def load_tourism_stats():
    """Load tourism economic data"""
    return pd.read_excel(DATA_PATHS['tourism_stats'])

def load_hotels():
    """Load hotel data with geo features"""
    hotels = pd.read_csv(DATA_PATHS['hotels'])
    return hotels[['NAME', 'ADDRESS', 'NUMROOMS', 'X', 'Y']].rename(columns={
        'X': 'longitude',
        'Y': 'latitude'
    })