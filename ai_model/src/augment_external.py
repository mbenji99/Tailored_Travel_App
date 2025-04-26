#!/usr/bin/env python3
"""
augment_external.py

Augments Scaled_Merged_Travel_Dataset.csv with:
  - current_temperature  (via python-weather, if installed)
  - currency_rate        (via currency_converter, if installed)
  - num_arrivals         (via FlightRadar24 API, if installed)
  - flight_price         (historical avg Transportation cost)
  - booking_price        (historical avg Accommodation cost)

This script does NOT require any of those optional libraries to be present.
"""

import os
import asyncio
import pandas as pd
from datetime import date
from dotenv import load_dotenv

# Optional imports—if missing, we’ll fallback gracefully
try:
    import python_weather
except ImportError:
    python_weather = None

try:
    from currency_converter import CurrencyConverter
except ImportError:
    CurrencyConverter = None

try:
    from FlightRadar24 import FlightRadar24API
except ImportError:
    FlightRadar24API = None

# ——— Load configuration ———
load_dotenv()  # read USER_CURRENCY, DEST_CURRENCY from project/.env

# Paths
BASE_DIR   = os.path.dirname(__file__)
INPUT_CSV  = os.path.abspath(os.path.join(BASE_DIR, '..', 'data', 'Scaled_Merged_Travel_Dataset.csv'))
OUTPUT_CSV = os.path.abspath(os.path.join(BASE_DIR, '..', 'data', 'Scaled_Merged_Travel_Dataset_augmented.csv'))

# Column that holds your “destination” identifier in the CSV
DEST_COL = 'location'  # adjust if your column is named differently

# Currency conversion settings (fallback to USD→EUR)
USER_CUR = os.getenv("USER_CURRENCY", "USD")
DEST_CUR = os.getenv("DEST_CURRENCY", "EUR")

def fetch_weather(dest: str) -> float:
    """Return current temperature (°F) or 0.0 if python-weather not available."""
    if python_weather is None:
        return 0.0
    try:
        client = python_weather.Client(format=python_weather.Imperial)
        w = asyncio.run(client.get(dest))
        client.close()
        return w.current.temperature or 0.0
    except:
        return 0.0

def fetch_currency_rate() -> float:
    """Return 1 USER_CUR → DEST_CUR, or 1.0 if currency_converter not available."""
    if CurrencyConverter is None:
        return 1.0
    try:
        cc = CurrencyConverter()
        return cc.convert(1, USER_CUR, DEST_CUR)
    except:
        return 1.0

def fetch_arrivals(dest_code: str) -> int:
    """Return number of incoming flights, or 0 if FlightRadar24API not available."""
    if FlightRadar24API is None:
        return 0
    try:
        fr = FlightRadar24API()
        flights = fr.get_flights(arrivalAirport=dest_code)
        return len(flights)
    except:
        return 0

def main():
    # 1) Load your existing scaled dataset
    df = pd.read_csv(INPUT_CSV, low_memory=False)

    # 2) Build list of unique destinations
    uniq = df[DEST_COL].dropna().unique()

    # 3) Fetch real‑time maps (or fallback values)
    weather_map   = {d: fetch_weather(d)   for d in uniq}
    arrivals_map  = {d: fetch_arrivals(d)  for d in uniq}
    currency_rate = fetch_currency_rate()

    # 4) Compute historical averages from your own data
    hist = (
        df.groupby(DEST_COL)
          .agg({
              'Transportation cost': 'mean',
              'Accommodation cost':  'mean'
          })
          .rename(columns={
              'Transportation cost':  'avg_transport_cost',
              'Accommodation cost':   'avg_accommodation_cost'
          })
    )
    transport_map     = hist['avg_transport_cost'].to_dict()
    accommodation_map = hist['avg_accommodation_cost'].to_dict()

    # 5) Add the new feature columns
    df['current_temperature'] = df[DEST_COL].map(weather_map).fillna(0.0)
    df['currency_rate']       = currency_rate
    df['num_arrivals']        = df[DEST_COL].map(arrivals_map).fillna(0).astype(int)
    df['flight_price']        = df[DEST_COL].map(transport_map).fillna(0.0)
    df['booking_price']       = df[DEST_COL].map(accommodation_map).fillna(0.0)

    # 6) Save the augmented CSV
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f" Augmented dataset written to: {OUTPUT_CSV}")

if __name__ == '__main__':
    main()
