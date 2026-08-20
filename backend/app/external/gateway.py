import httpx
import logging

logger = logging.getLogger(__name__)

CITY_COORDINATES = {
    "tokyo": {"lat": 35.6762, "lon": 139.6503},
    "paris": {"lat": 48.8566, "lon": 2.3522},
    "london": {"lat": 51.5074, "lon": -0.1278},
    "new york": {"lat": 40.7128, "lon": -74.0060},
    "rome": {"lat": 41.9028, "lon": 12.4964},
}

WMO_DESCRIPTIONS = {
    0: "Clear sky ☀️",
    1: "Mainly clear 🌤️",
    2: "Partly cloudy ⛅",
    3: "Overcast ☁️",
    45: "Foggy 🌫️",
    48: "Depositing rime fog 🌫️",
    51: "Light drizzle 🌧️",
    53: "Moderate drizzle 🌧️",
    55: "Dense drizzle 🌧️",
    61: "Slight rain 🌧️",
    63: "Moderate rain 🌧️",
    65: "Heavy rain 🌧️",
    71: "Slight snow fall ❄️",
    73: "Moderate snow fall ❄️",
    75: "Heavy snow fall ❄️",
    77: "Snow grains ❄️",
    80: "Slight rain showers 🌦️",
    81: "Moderate rain showers 🌦️",
    82: "Violent rain showers ⛈️",
    85: "Slight snow showers 🌨️",
    86: "Heavy snow showers 🌨️",
    95: "Thunderstorm 🌩️",
}

class WeatherGateway:
    """
    Gateway to fetch live weather reports from Open-Meteo.
    Throws ValueError for unknown destinations and communicates failures directly.
    """

    @staticmethod
    def get_weather_report(destination: str) -> dict:
        dest_clean = destination.strip().lower()
        coords = None
        for city, location in CITY_COORDINATES.items():
            if city in dest_clean:
                coords = location
                break

        if not coords:
            raise ValueError(f"Destination '{destination}' coordinates not found. Supported: Tokyo, Paris, London, Rome, New York.")

        url = f"https://api.open-meteo.com/v1/forecast?latitude={coords['lat']}&longitude={coords['lon']}&current_weather=true"
        
        try:
            # Synchronous HTTP call with a strict timeout (5 seconds)
            response = httpx.get(url, timeout=5.0)
            if response.status_code != 200:
                raise RuntimeError(f"Open-Meteo returned status code {response.status_code}")
            
            data = response.json()
            current = data.get("current_weather", {})
            if not current:
                raise RuntimeError("Weather response missing 'current_weather' details")

            temp = current.get("temperature")
            wind = current.get("windspeed")
            code = current.get("weathercode", 0)

            return {
                "destination": destination,
                "temperature": temp,
                "windspeed": wind,
                "conditions": WMO_DESCRIPTIONS.get(code, "Mild weather"),
                "provider": "Open-Meteo API"
            }
        except httpx.RequestError as e:
            logger.error(f"Network error calling Open-Meteo: {e}")
            raise RuntimeError(f"Network connection failed: {str(e)}")
        except Exception as e:
            logger.error(f"Error parsing weather: {e}")
            raise RuntimeError(f"Failed to fetch weather: {str(e)}")
