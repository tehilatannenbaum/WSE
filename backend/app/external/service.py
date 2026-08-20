import httpx
import logging
from fastapi import APIRouter, HTTPException, Query
from backend.app.config import settings

# Optional Cloudinary imports
cloudinary_available = False
try:
    if settings.CLOUDINARY_URL and settings.CLOUDINARY_URL.strip():
        import cloudinary
        import cloudinary.uploader
        # Cloudinary automatically parses CLOUDINARY_URL from env if set
        cloudinary_available = True
except ImportError:
    pass

router = APIRouter(prefix="/external", tags=["external"])
logger = logging.getLogger(__name__)

# City coordinate mapping for weather forecasts
CITY_COORDINATES = {
    "tokyo": {"lat": 35.6762, "lon": 139.6503},
    "paris": {"lat": 48.8566, "lon": 2.3522},
    "london": {"lat": 51.5074, "lon": -0.1278},
    "new york": {"lat": 40.7128, "lon": -74.0060},
    "rome": {"lat": 41.9028, "lon": 12.4964},
}

DEFAULT_COORDINATES = {"lat": 32.0853, "lon": 34.7818} # Tel Aviv

# Weather code descriptions (WMO weather interpretation codes)
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

@router.get("/weather")
async def get_weather(destination: str = Query(..., min_length=2)):
    # Clean string
    dest_clean = destination.strip().lower()
    
    # Resolve coordinates
    coords = None
    for city, location in CITY_COORDINATES.items():
        if city in dest_clean:
            coords = location
            break
            
    if not coords:
        # Defaults to default coordinates if destination is unknown
        coords = DEFAULT_COORDINATES
        
    url = f"https://api.open-meteo.com/v1/forecast?latitude={coords['lat']}&longitude={coords['lon']}&current_weather=true"
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            if response.status_code != 200:
                raise HTTPException(status_code=502, detail="Failed to fetch weather from external provider")
                
            data = response.json()
            current = data.get("current_weather", {})
            temp = current.get("temperature", 22.0)
            wind = current.get("windspeed", 10.0)
            weather_code = current.get("weathercode", 0)
            
            description = WMO_DESCRIPTIONS.get(weather_code, "Mild weather")
            
            return {
                "destination": destination,
                "temperature": temp,
                "windspeed": wind,
                "conditions": description,
                "provider": "Open-Meteo API"
            }
    except Exception as e:
        logger.error(f"Weather service error: {e}")
        # Return fallback mock weather to keep application operational if offline
        return {
            "destination": destination,
            "temperature": 22.5,
            "windspeed": 8.5,
            "conditions": "Partly cloudy ⛅ (Offline Mode)",
            "provider": "Mock Fallback Service"
        }

@router.post("/upload-image")
def upload_image(image_base64: str):
    """
    Optional Cloudinary upload endpoint.
    If Cloudinary is configured via CLOUDINARY_URL in .env, uploads the image.
    Otherwise, returns a local mock asset url.
    """
    if cloudinary_available:
        try:
            # Upload base64 encoded image
            upload_result = cloudinary.uploader.upload(image_base64)
            return {
                "status": "Success",
                "image_url": upload_result.get("secure_url"),
                "provider": "Cloudinary"
            }
        except Exception as e:
            logger.error(f"Cloudinary upload failed: {e}")
            raise HTTPException(status_code=500, detail=f"Cloudinary upload error: {str(e)}")
    
    # Fallback mock image url
    return {
        "status": "Success",
        "image_url": "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=500",
        "provider": "Mock Storage (No Cloudinary Configured)"
    }
