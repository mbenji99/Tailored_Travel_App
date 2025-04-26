
import pandas as pd
from data_config import DATA_PATHS

def load_trips():
    """Load trip details (already cleaned & standardized) and synthesize a rating."""
    df = pd.read_csv(DATA_PATHS["traveler_trips"], low_memory=False)
    df["rating"] = (
        df["Duration (days)"] 
        / df["Duration (days)"].max() 
        * 5
    ).round(1)
    return (
        df[["Traveler name", "Destination", "rating"]]
          .rename(columns={
             "Traveler name": "user_id",
             "Destination"  : "item_id"
          })
    )

def load_expedia():
    """Load full Expedia search log for analytics or feature‐building."""
    return pd.read_csv(DATA_PATHS["expedia"], low_memory=False)

def load_travel_activity():
    """Load your standardized travel/activity log (if distinct from trips)."""
    return pd.read_csv(DATA_PATHS["travel"], low_memory=False)

def load_destinations():
    """
    Build a lookup of destination → country from the Expedia search logs,
    used by content‑based filtering.
    """
    exp = load_expedia()
    return (
        exp.groupby("srch_destination_id")
           .first()
           .reset_index()[["srch_destination_id", "hotel_country"]]
    )

def load_tourism_stats():
    """
    Load standardized tourism/economic stats (CSV) for clustering or enrichment.
    """
    return pd.read_csv(DATA_PATHS["toursat"], low_memory=False)

def load_hotels():
    """
    Load standardized hotel master list with geo and size flags.
    """
    df = pd.read_csv(DATA_PATHS["hotels"], low_memory=False)
    return (
        df[[
            "Hotel_Name",
            "Address",
            "Num_Rooms",
            "Longitude",
            "Latitude",
            "is_large_hotel",
            "has_coordinates",
        ]]
        .rename(columns={
            "Hotel_Name": "name",
            "Num_Rooms" : "num_rooms",
            "Longitude" : "longitude",
            "Latitude"  : "latitude",
        })
    )
