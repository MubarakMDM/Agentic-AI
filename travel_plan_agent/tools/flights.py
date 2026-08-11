"""
Flights tool — backed by the real Duffel API (https://duffel.com/docs).

NOTE: This replaces an earlier Amadeus-based version. Amadeus decommissioned
its free Self-Service API portal on July 17, 2026 (existing keys deactivated,
portal inaccessible). Duffel is the recommended migration path: no
IATA/ARC accreditation needed for search, simple bearer-token auth (no
OAuth2 dance), and a free test mode.

Setup:
    pip install requests python-dotenv
    1. Sign up at https://duffel.com (free)
    2. In your dashboard, switch to "Developer test mode" and create an
       access token — test tokens start with `duffel_test_`
    3. Put it in a .env file at your project root (never commit it):
        DUFFEL_ACCESS_TOKEN=duffel_test_xxxxxxxxxxxxx

Two real API calls happen here:
    1. Places Suggestions -> resolve a city/airport name to an IATA code
    2. Offer Requests      -> real (sandboxed) fare data for that route/date

Important caveat: in test mode, searches are served by "Duffel Airways" —
a sandbox airline with predictable but NOT realistic prices or schedules
(same trade-off Amadeus test data had). Switch to a live token
(`duffel_live_...`) later for real fares; pricing is pay-per-booking, not
a fixed subscription.
Docs: https://duffel.com/docs/guides/getting-started-with-flights
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

DUFFEL_ACCESS_TOKEN = os.getenv("DUFFEL_ACCESS_TOKEN")

BASE_URL = "https://api.duffel.com"
PLACES_URL = f"{BASE_URL}/places/suggestions"
OFFER_REQUESTS_URL = f"{BASE_URL}/air/offer_requests"

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Duffel-Version": "v2",
}

# IATA-code cache (in-process; fine for a single agent run/session)
_iata_cache: dict[str, str] = {}


def _auth_headers() -> dict:
    if not DUFFEL_ACCESS_TOKEN:
        raise RuntimeError(
            "DUFFEL_ACCESS_TOKEN not set. Add it to your .env file. "
            "Get one free at https://duffel.com (Developer test mode)."
        )
    return {**HEADERS, "Authorization": f"Bearer {DUFFEL_ACCESS_TOKEN}"}


def _resolve_iata_code(city_or_airport: str) -> str | None:
    """Resolves a free-text city or airport name to an IATA code using
    Duffel's Places Suggestions endpoint. Prefers a city-level code (covers
    all airports in that city, e.g. "LON") over a single airport when both
    are returned. Returns None if nothing matches. Cached per input."""
    cache_key = city_or_airport.strip().lower()
    if cache_key in _iata_cache:
        return _iata_cache[cache_key]

    # Already looks like an IATA code (3 letters) — use as-is.
    if len(city_or_airport.strip()) == 3 and city_or_airport.strip().isalpha():
        code = city_or_airport.strip().upper()
        _iata_cache[cache_key] = code
        return code

    resp = requests.get(
        PLACES_URL,
        params={"query": city_or_airport},
        headers=_auth_headers(),
        timeout=10,
    )
    resp.raise_for_status()
    results = resp.json().get("data", [])
    if not results:
        return None

    # Prefer a "city" type result over an "airport" — a city code lets
    # Duffel search across all of that city's airports at once.
    city_match = next((r for r in results if r.get("type") == "city"), None)
    top = city_match or results[0]

    code = top["iata_code"]
    _iata_cache[cache_key] = code
    return code


def get_ticket_price(origin: str, destination: str, travel_date: str,
                      adults: int = 1) -> dict:
    """Looks up real flight fares between two cities on a given date using
    the Duffel API (test mode = Duffel Airways sandbox data).

    Args:
        origin: Departure city or airport name, e.g. "Paris" or "CDG".
        destination: Arrival city or airport name, e.g. "London" or "LHR".
        travel_date: Departure date, format YYYY-MM-DD. Required.
        adults: Number of adult passengers (default 1).

    Returns:
        dict with:
            status: "success" | "origin_not_found" | "destination_not_found"
                    | "no_flights_found" | "error"
            origin_code, destination_code: resolved IATA codes
            cheapest_price, currency
            offers: up to 5 offers, each with price, currency, and airline name
    """
    try:
        origin_code = _resolve_iata_code(origin)
    except (requests.RequestException, RuntimeError) as e:
        return {"status": "error", "message": f"Failed to resolve origin: {e}"}
    if origin_code is None:
        return {"status": "origin_not_found", "message": f"No airport/city found for '{origin}'."}

    try:
        destination_code = _resolve_iata_code(destination)
    except (requests.RequestException, RuntimeError) as e:
        return {"status": "error", "message": f"Failed to resolve destination: {e}"}
    if destination_code is None:
        return {"status": "destination_not_found", "message": f"No airport/city found for '{destination}'."}

    body = {
        "data": {
            "slices": [{
                "origin": origin_code,
                "destination": destination_code,
                "departure_date": travel_date,
            }],
            "passengers": [{"type": "adult"} for _ in range(adults)],
            "cabin_class": "economy",
        }
    }

    try:
        resp = requests.post(
            OFFER_REQUESTS_URL,
            params={"return_offers": "true", "supplier_timeout": 15000},
            json=body,
            headers=_auth_headers(),
            timeout=20,
        )
        resp.raise_for_status()
        offers = resp.json()["data"].get("offers", [])
    except requests.HTTPError as e:
        detail = ""
        try:
            errs = e.response.json().get("errors", [])
            detail = "; ".join(f"{er.get('title')}: {er.get('message')}" for er in errs)
        except Exception:
            pass
        return {"status": "error", "message": f"Flight search failed: {e}. {detail}"}
    except (requests.RequestException, RuntimeError) as e:
        return {"status": "error", "message": f"Flight search failed: {e}"}

    if not offers:
        return {
            "status": "no_flights_found",
            "origin_code": origin_code,
            "destination_code": destination_code,
            "message": f"No flight offers found for {origin_code} -> {destination_code} on {travel_date}.",
        }

    parsed_offers = [
        {
            "price": float(o["total_amount"]),
            "currency": o["total_currency"],
            "airline": o.get("owner", {}).get("name", "Unknown"),
        }
        for o in offers[:5]
    ]
    cheapest = min(parsed_offers, key=lambda o: o["price"])

    return {
        "status": "success",
        "origin_code": origin_code,
        "destination_code": destination_code,
        "travel_date": travel_date,
        "cheapest_price": cheapest["price"],
        "currency": cheapest["currency"],
        "offers": parsed_offers,
    }


if __name__ == "__main__":
    # Quick manual test — run with: python flights.py
    # Requires DUFFEL_ACCESS_TOKEN in a .env file.
    import json
    print(json.dumps(get_ticket_price("Paris", "London", "2026-09-15"), indent=2))