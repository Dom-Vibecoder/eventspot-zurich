"""Geocode addresses/venue names to lat/lng using Google Maps Geocoding API."""

import requests
import time

# Uses the same Google Cloud project as EventSpot's Maps JS API.
# The Geocoding API must be enabled in Google Cloud Console.
MAPS_API_KEY = "AIzaSyB_fNBv6ZLw5wm9fKwGeJ12L4p6sVM0hQg"

# Simple in-memory cache to avoid redundant API calls within a single run
_cache = {}

# Default: Zürich city center
DEFAULT_LAT = 47.3769
DEFAULT_LNG = 8.5417


def geocode(address, region_hint="Zürich, Schweiz"):
    """Convert an address or venue name to (lat, lng).

    Appends region_hint to improve accuracy for local venues.
    Returns (lat, lng) tuple, or default Zürich center if geocoding fails.
    """
    if not address:
        return DEFAULT_LAT, DEFAULT_LNG

    cache_key = address.strip().lower()
    if cache_key in _cache:
        return _cache[cache_key]

    query = f"{address}, {region_hint}" if region_hint else address

    try:
        resp = requests.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={"address": query, "key": MAPS_API_KEY},
            timeout=10,
        )
        data = resp.json()

        if data.get("status") == "OK" and data.get("results"):
            loc = data["results"][0]["geometry"]["location"]
            result = (loc["lat"], loc["lng"])
            _cache[cache_key] = result
            return result

        print(f"  [geocode] No result for '{address}': {data.get('status')}")
    except Exception as e:
        print(f"  [geocode] Error for '{address}': {e}")

    # Rate limit: be respectful
    time.sleep(0.2)

    _cache[cache_key] = (DEFAULT_LAT, DEFAULT_LNG)
    return DEFAULT_LAT, DEFAULT_LNG
