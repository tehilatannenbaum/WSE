import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.database import init_db, SessionLocal, FlightRead
from backend.app.gateway.router import gateway_router
from backend.app.ai.rag_service import init_rag

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Flight Booking & Travel Assistant Backend Gateway",
    description="FastAPI CQRS/Event-Sourced travel backend with API Gateway and Ollama RAG integration",
    version="1.0.0"
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the main API Gateway router
app.include_router(gateway_router)

@app.on_event("startup")
def startup_event():
    logger.info("Initializing system...")
    
    # 1. Initialize databases
    init_db()
    
    # 2. Seed Flight schedules if empty
    db = SessionLocal()
    try:
        if db.query(FlightRead).count() == 0:
            logger.info("Seeding flight read models...")
            seeds = [
                FlightRead(
                    flight_number="LY-101",
                    origin="Tel Aviv",
                    destination="Paris",
                    departure_time="2026-08-25 08:30",
                    price=299.00,
                    available_seats=45,
                    image_url="https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=500"
                ),
                FlightRead(
                    flight_number="LY-202",
                    origin="Tel Aviv",
                    destination="Tokyo",
                    departure_time="2026-08-26 22:15",
                    price=899.50,
                    available_seats=60,
                    image_url="https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=500"
                ),
                FlightRead(
                    flight_number="LY-303",
                    origin="Tel Aviv",
                    destination="London",
                    departure_time="2026-08-27 11:00",
                    price=349.99,
                    available_seats=32,
                    image_url="https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=500"
                ),
                FlightRead(
                    flight_number="LY-404",
                    origin="Tel Aviv",
                    destination="New York",
                    departure_time="2026-08-28 06:45",
                    price=650.00,
                    available_seats=75,
                    image_url="https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=500"
                ),
                FlightRead(
                    flight_number="LY-505",
                    origin="Tel Aviv",
                    destination="Rome",
                    departure_time="2026-08-29 15:30",
                    price=180.00,
                    available_seats=18,
                    image_url="https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=500"
                )
            ]
            db.bulk_save_objects(seeds)
            db.commit()
            logger.info("Flight models successfully seeded.")
    except Exception as e:
        logger.error(f"Error during flight seeding: {e}")
        db.rollback()
    finally:
        db.close()
        
    # 3. Initialize RAG embeddings and load knowledge base
    init_rag()
    logger.info("Startup sequence completed successfully.")

@app.get("/")
def read_root():
    return {
        "status": "Healthy",
        "service": "Flight & Travel Assistant Gateway Server",
        "version": "1.0.0",
        "documentation": "/docs"
    }

@app.get("/health")
def health_check():
    return {
        "status": "Healthy",
        "service": "Flight & Travel Assistant Gateway Server",
        "version": "1.0.0"
    }
