from fastapi import APIRouter, HTTPException, Query
from backend.app.external.gateway import WeatherGateway

router = APIRouter(prefix="/external", tags=["external"])

@router.get("/weather")
def get_weather(destination: str = Query(..., min_length=2)):
    """
    Get weather forecast for a destination city.
    Delegates coordinates resolution and external API fetching to WeatherGateway.
    """
    try:
        report = WeatherGateway.get_weather_report(destination)
        return report
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
