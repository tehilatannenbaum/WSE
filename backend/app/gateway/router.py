from fastapi import APIRouter
from backend.app.auth.service import router as auth_router
from backend.app.flights.service import router as flights_router
from backend.app.bookings.service import router as bookings_router
from backend.app.external.service import router as external_router
from backend.app.ai.rag_service import router as ai_router

# The API Gateway Router aggregates all microservices/domain routers.
gateway_router = APIRouter(prefix="/api")

# Mount sub-routers
gateway_router.include_router(auth_router)
gateway_router.include_router(flights_router)
gateway_router.include_router(bookings_router)
gateway_router.include_router(external_router)
gateway_router.include_router(ai_router)
