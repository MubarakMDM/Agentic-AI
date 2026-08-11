"""
Distance tool — backed by Open-Meteo's geocoding API
(https://open-meteo.com/en/docs/geocoding-api), which is free, requires
NO API key, and (unlike Nominatim) is built for application/backend use
rather than occasional human lookups — so it doesn't rate-limit or block
server traffic the way Nominatim can. Distance itself is computed locally
with the haversine formula.
"""

import math

import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
EARTH_RADIUS_KM = 6371.0

# In-process cache so repeated lookups (e.g. the same city asked twice in
# a session) don't re-hit the API.
_geocode_cache: dict[str, dict] = {}


def _geocode_city(city: str) -> dict | None:
    """Resolves a city name to {name, country, latitude, longitude} using
    Open-Meteo's geocoding endpoint. Returns None if not found. Cached
    per city."""
    cache_key = city.strip().lower()
    if cache_key in _geocode_cache:
        return _geocode_cache[cache_key]

    resp = requests.get(
        GEOCODING_URL,
        params={"name": city, "count": 1, "language": "en", "format": "json"},
        timeout=10,
    )
    resp.raise_for_status()
    results = resp.json().get("results")
    if not results:
        return None

    top = results[0]
    location = {
        "name": top["name"],
        "country": top.get("country", ""),
        "latitude": top["latitude"],
        "longitude": top["longitude"],
    }
    _geocode_cache[cache_key] = location
    return location


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two lat/lon points, in kilometers."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def calculate_distance(origin: str, destination: str) -> dict:
    """Calculates the real great-circle (straight-line) distance between
    two cities, in kilometers and miles.

    Uses Open-Meteo's geocoding API (free, no API key) to geocode each
    city, then computes the haversine distance locally. Note this is
    straight-line "as the crow flies" distance, not driving/flight route
    distance — good enough for budget/feasibility checks, not for
    turn-by-turn routing.

    Args:
        origin: Departure city name, e.g. "Paris" or "Paris, France".
        destination: Arrival city name.

    Returns:
        dict with:
            status: "success" | "origin_not_found" | "destination_not_found" | "error"
            origin, destination: resolved display names
            distance_km, distance_miles: straight-line distance
    """
    try:
        origin_loc = _geocode_city(origin)
    except (requests.RequestException, ValueError) as e:
        return {"status": "error", "message": f"Geocoding request failed for origin: {e}"}

    if origin_loc is None:
        return {
            "status": "origin_not_found",
            "message": f"Could not find a location matching '{origin}'.",
        }

    try:
        dest_loc = _geocode_city(destination)
    except (requests.RequestException, ValueError) as e:
        return {"status": "error", "message": f"Geocoding request failed for destination: {e}"}

    if dest_loc is None:
        return {
            "status": "destination_not_found",
            "message": f"Could not find a location matching '{destination}'.",
        }

    distance_km = _haversine_km(
        origin_loc["latitude"], origin_loc["longitude"],
        dest_loc["latitude"], dest_loc["longitude"],
    )

    return {
        "status": "success",
        "origin": origin_loc["name"],
        "destination": dest_loc["name"],
        "distance_km": round(distance_km, 1),
        "distance_miles": round(distance_km * 0.621371, 1),
    }


if __name__ == "__main__":
    # Quick manual test — run with: python distance.py
    import json
    print(json.dumps(calculate_distance("Paris", "London"), indent=2))
    print(json.dumps(calculate_distance("Tokyo", "New York"), indent=2))