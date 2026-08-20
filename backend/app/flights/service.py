from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.database import get_db, FlightRead

router = APIRouter(prefix="/flights", tags=["flights"])

# Schemas
class FlightResponse(BaseModel):
    id: int
    flight_number: str
    origin: str
    destination: str
    departure_time: str
    price: float
    available_seats: int
    image_url: str | None

    class Config:
        from_attributes = True

# API Routes
@router.get("/search", response_model=list[FlightResponse])
def search_flights(
    origin: str | None = None,
    destination: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(FlightRead)
    
    if origin and origin.strip():
        query = query.filter(FlightRead.origin.ilike(f"%{origin.strip()}%"))
    if destination and destination.strip():
        query = query.filter(FlightRead.destination.ilike(f"%{destination.strip()}%"))
        
    return query.all()

@router.get("/{flight_id}", response_model=FlightResponse)
def get_flight(flight_id: int, db: Session = Depends(get_db)):
    flight = db.query(FlightRead).filter(FlightRead.id == flight_id).first()
    if not flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flight not found"
        )
    return flight
