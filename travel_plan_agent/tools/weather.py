"""
Weather tool — backed by Open-Meteo (https://open-meteo.com), which is
free and requires NO API key. Two calls are made:

    1. Geocoding API  -> resolve a city name to lat/lon
    2. Forecast API   -> get the daily forecast for that lat/lon

Docs:
    https://open-meteo.com/en/docs/geocoding-api
    https://open-meteo.com/en/docs
"""

from datetime import datetime, timedelta

import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# WMO Weather interpretation codes -> human-readable text
# https://open-meteo.com/en/docs (see "WMO Weather interpretation codes")
WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    56: "Light freezing drizzle", 57: "Dense freezing drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    66: "Light freezing rain", 67: "Heavy freezing rain",
    71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    85: "Slight snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
}


def _geocode_city(city: str) -> dict | None:
    """Resolves a city name to {name, country, latitude, longitude} using
    Open-Meteo's free geocoding endpoint. Returns None if not found."""
    resp = requests.get(
        GEOCODING_URL,
        params={"name": city, "count": 1, "language": "en", "format": "json"},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    results = data.get("results")
    if not results:
        return None

    top = results[0]
    return {
        "name": top["name"],
        "country": top.get("country", ""),
        "latitude": top["latitude"],
        "longitude": top["longitude"],
    }


def get_weather(city: str, forecast_days: int = 10, travel_date: str = "") -> dict:
    """Gets a real weather forecast for a city.

    Uses Open-Meteo (free, no API key). Choose forecast_days=2 for a
    short-range forecast (most accurate, best for imminent travel) or
    forecast_days=10 for a longer-range outlook (less precise the further
    out it goes). If travel_date falls outside the returned window, a note
    explains that and the full available window is still returned.

    Args:
        city: City name, e.g. "Paris" or "New York".
        forecast_days: Either 2 (short-range) or 10 (longer-range). Any
            other value is clamped to the nearest of these two.
        travel_date: Optional date string in YYYY-MM-DD format, used to
            highlight the matching day in the result.

    Returns:
        dict with:
            status: "success" | "city_not_found" | "error"
            city, country, latitude, longitude, forecast_days
            forecast: list of {date, condition, temp_max_c, temp_min_c,
                                precipitation_probability_pct}
            requested_date_forecast: the single day matching travel_date, if any
            note: extra context, e.g. if the requested date was out of range
    """
    # Only two supported windows — clamp anything else to the closer one.
    forecast_days = 2 if abs(forecast_days - 2) <= abs(forecast_days - 10) else 10

    try:
        location = _geocode_city(city)
    except requests.RequestException as e:
        return {"status": "error", "message": f"Geocoding request failed: {e}"}

    if location is None:
        return {
            "status": "city_not_found",
            "message": f"Could not find a location matching '{city}'.",
        }

    note = ""
    today = datetime.now().date()
    max_forecast_date = today + timedelta(days=forecast_days - 1)

    if travel_date:
        try:
            requested_date = datetime.strptime(travel_date, "%Y-%m-%d").date()
        except ValueError:
            return {
                "status": "error",
                "message": f"travel_date '{travel_date}' is not in YYYY-MM-DD format.",
            }
        if requested_date > max_forecast_date:
            note = (
                f"'{travel_date}' is beyond the {forecast_days}-day window — "
                f"showing the available forecast instead. Call again with "
                f"forecast_days=10 if you need to look further out."
            )
        elif requested_date < today:
            note = f"'{travel_date}' is in the past — showing the upcoming forecast instead."

    try:
        resp = requests.get(
            FORECAST_URL,
            params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "daily": "weathercode,temperature_2m_max,temperature_2m_min,"
                         "precipitation_probability_max",
                "timezone": "auto",
                "forecast_days": forecast_days,
            },
            timeout=10,
        )
        resp.raise_for_status()
        daily = resp.json()["daily"]
    except (requests.RequestException, KeyError) as e:
        return {"status": "error", "message": f"Forecast request failed: {e}"}

    forecast = []
    for i, date_str in enumerate(daily["time"]):
        code = daily["weathercode"][i]
        forecast.append({
            "date": date_str,
            "condition": WMO_CODES.get(code, f"Unknown (code {code})"),
            "temp_max_c": daily["temperature_2m_max"][i],
            "temp_min_c": daily["temperature_2m_min"][i],
            "precipitation_probability_pct": daily["precipitation_probability_max"][i],
        })

    # If a specific in-range date was requested, trim to just that day
    # (plus keep the full list available for context).
    single_day = None
    if travel_date and not note:
        single_day = next((f for f in forecast if f["date"] == travel_date), None)

    return {
        "status": "success",
        "city": location["name"],
        "country": location["country"],
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "forecast_days": forecast_days,
        "requested_date_forecast": single_day,
        "forecast": forecast,
        "note": note,
    }


if __name__ == "__main__":
    # Quick manual test — run with: python weather.py
    import json
    print(json.dumps(get_weather("Paris", forecast_days=10, travel_date="2026-08-10"), indent=2))
    print(json.dumps(get_weather("Paris", forecast_days=2), indent=2))