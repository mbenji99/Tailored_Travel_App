import os


HERE = os.path.dirname(__file__)
DATA_DIR = os.path.normpath(os.path.join(HERE, "..", "data"))

DATA_PATHS = {
    "traveler_trips": os.path.join(DATA_DIR, "Standardized_TravelerTripDataset.csv"),
    "expedia":        os.path.join(DATA_DIR, "Standardized_ExpediaDataset.csv"),
    "hotels":         os.path.join(DATA_DIR, "Standardized_Hotels.csv"),
    "toursat":        os.path.join(DATA_DIR, "Standardized_TourSat2023.csv"),
    "travel":         os.path.join(DATA_DIR, "Standardized_Travel.csv"),
}
