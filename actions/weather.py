"""
actions/weather.py
==================
Fetches current weather information using the free Open-Meteo API.
Requires no API key.
"""
from __future__ import annotations
import requests
from utils.logger import get_logger

logger = get_logger(__name__)


def get_weather(location: str = "") -> str:
    """
    Fetch current weather for *location* (or default location).
    """
    city = (location or "").strip()
    if not city:
        city = "London"  # Default city fallback

    try:
        # Step 1: Geocode city name to lat/lon
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_res = requests.get(geo_url, timeout=5).json()

        results = geo_res.get("results")
        if not results:
            logger.warning(f"Could not find coordinates for city: {city}")
            return f"Sorry, I could not find weather information for {city}."

        first_match = results[0]
        lat = first_match["latitude"]
        lon = first_match["longitude"]
        matched_name = first_match.get("name", city)

        # Step 2: Fetch current weather
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current_weather=true"
        )
        weather_res = requests.get(weather_url, timeout=5).json()
        current = weather_res.get("current_weather")

        if not current:
            return f"Sorry, weather data is currently unavailable for {matched_name}."

        temp = current.get("temperature")
        wind = current.get("windspeed")
        code = current.get("weathercode", 0)

        # Basic WMO weather code mapping
        conditions = {
            0: "clear skies",
            1: "mainly clear",
            2: "partly cloudy",
            3: "overcast",
            45: "foggy",
            48: "depositing rime fog",
            51: "light drizzle",
            61: "slight rain",
            63: "moderate rain",
            65: "heavy rain",
            71: "slight snow",
            80: "rain showers",
            95: "thunderstorm",
        }
        condition_str = conditions.get(code, "cloudy")

        msg = f"In {matched_name}, it is currently {temp} degrees Celsius with {condition_str} and wind speeds of {wind} km/h."
        logger.info(msg)
        return msg

    except Exception as e:
        logger.error(f"Failed to fetch weather for '{city}': {e}")
        return f"Sorry, I was unable to retrieve the weather for {city}."
