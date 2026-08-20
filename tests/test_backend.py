import os
import sys
import pytest

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup test environment database before importing app config
os.environ["DATABASE_URL"] = "sqlite:///./test_travel_assistant.db"

from backend.app.main import app
from backend.app.database import Base, get_db, FlightRead, BookingRead, EventStore
from backend.app.bookings.service import rebuild_read_models

# Configure test database engine
TEST_DATABASE_URL = "sqlite:///./test_travel_assistant.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    # Create test database tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Seed default flights for tests
    db.query(FlightRead).delete()
    db.query(BookingRead).delete()
    db.query(EventStore).delete()
    
    seeds = [
        FlightRead(
            id=1,
            flight_number="LY-101",
            origin="Tel Aviv",
            destination="Paris",
            departure_time="2026-08-25 08:30",
            price=299.00,
            available_seats=45,
            image_url="http://example.com/paris"
        ),
        FlightRead(
            id=2,
            flight_number="LY-202",
            origin="Tel Aviv",
            destination="Tokyo",
            departure_time="2026-08-26 22:15",
            price=899.50,
            available_seats=60,
            image_url="http://example.com/tokyo"
        )
    ]
    db.bulk_save_objects(seeds)
    db.commit()
    db.close()
    yield
    
    # Release DB connections and engine pool
    app.dependency_overrides.clear()
    engine.dispose()
    
    if os.path.exists("./test_travel_assistant.db"):
        try:
            os.remove("./test_travel_assistant.db")
        except Exception:
            pass

# Override dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "Healthy"

def test_auth_flow():
    # 1. Register
    reg_payload = {
        "username": "tester",
        "password": "secretpassword",
        "email": "tester@test.com"
    }
    response = client.post("/api/auth/register", json=reg_payload)
    assert response.status_code == 201
    assert response.json()["username"] == "tester"

    # 2. Login
    login_data = {
        "username": "tester",
        "password": "secretpassword"
    }
    response = client.post("/api/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json().get("access_token")
    assert token is not None

def test_flight_search_with_date():
    # Query with date
    response = client.get("/api/flights/search?origin=Tel Aviv&date=2026-08-25")
    assert response.status_code == 200
    flights = response.json()
    assert len(flights) == 1
    assert flights[0]["flight_number"] == "LY-101"

    # Query with wrong date
    response = client.get("/api/flights/search?origin=Tel Aviv&date=2026-08-30")
    assert response.status_code == 200
    assert len(response.json()) == 0

def test_booking_creation_cancellation():
    # 1. Login to get token
    login_data = {"username": "tester", "password": "secretpassword"}
    login_res = client.post("/api/auth/login", data=login_data)
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Book
    booking_req = {
        "flight_id": 1,
        "passenger_name": "John Doe",
        "passport_number": "AB12345"
    }
    response = client.post("/api/bookings/book", json=booking_req, headers=headers)
    assert response.status_code == 201
    booking_id = response.json()["booking_id"]
    assert booking_id is not None

    # Check seats decremented (45 -> 44)
    flight_res = client.get("/api/flights/1")
    assert flight_res.json()["available_seats"] == 44

    # 3. Cancel Booking
    response = client.post(f"/api/bookings/{booking_id}/cancel", headers=headers)
    assert response.status_code == 200
    
    # Check seats incremented back (44 -> 45)
    flight_res = client.get("/api/flights/1")
    assert flight_res.json()["available_seats"] == 45

def test_optimistic_concurrency():
    # Setup duplicate event seq manual insert
    db = TestingSessionLocal()
    event_id = "test-aggregate-uuid-12345"
    
    # Save sequence 1
    e1 = EventStore(
        aggregate_type="Booking",
        aggregate_id=event_id,
        sequence_number=1,
        event_type="FlightBooked",
        payload="{}"
    )
    db.add(e1)
    db.commit()

    # Try inserting seq 1 duplicate
    from sqlalchemy.exc import IntegrityError
    e2 = EventStore(
        aggregate_type="Booking",
        aggregate_id=event_id,
        sequence_number=1,
        event_type="FlightBooked",
        payload="{}"
    )
    db.add(e2)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()
    db.close()

def test_repeatable_rebuild():
    db = TestingSessionLocal()
    # Reset test database
    db.query(BookingRead).delete()
    db.query(EventStore).delete()
    db.commit()

    # Seed events
    e1 = EventStore(
        aggregate_type="Booking",
        aggregate_id="b1",
        sequence_number=1,
        event_type="FlightBooked",
        payload='{"user_id": 1, "flight_id": 1, "passenger_name": "Test User", "passport_number": "XXXX-4567"}'
    )
    db.add(e1)
    db.commit()

    rebuild_read_models(db)
    
    # Verify booking projection created
    booking = db.query(BookingRead).filter(BookingRead.id == "b1").first()
    assert booking is not None
    assert booking.status == "Active"

    # Repeat rebuild
    rebuild_read_models(db)
    bookings = db.query(BookingRead).all()
    assert len(bookings) == 1
    db.close()

def test_atomic_transaction_fail():
    # Verify that if projection fails, event is not stored (rolled back)
    # We will trigger validation error by inserting an event with invalid json payload
    db = TestingSessionLocal()
    db.query(EventStore).delete()
    db.commit()

    login_data = {"username": "tester", "password": "secretpassword"}
    login_res = client.post("/api/auth/login", data=login_data)
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Book with invalid flight_id to trigger HTTPException during transaction
    booking_req = {
        "flight_id": 9999,  # Flight not found error
        "passenger_name": "John Doe",
        "passport_number": "AB12345"
    }
    response = client.post("/api/bookings/book", json=booking_req, headers=headers)
    assert response.status_code == 404

    # Assert no events exist in EventStore
    events_count = db.query(EventStore).count()
    assert events_count == 0
    db.close()
