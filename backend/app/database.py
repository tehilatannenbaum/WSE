import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.config import settings

# Setup engine - handles both sqlite and postgresql URLs
# If SQLite, add check_same_thread configuration
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==========================================
# WRITE MODEL: Event Store Table
# ==========================================
class EventStore(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    aggregate_id = Column(String(50), nullable=False, index=True)
    aggregate_type = Column(String(50), nullable=False)
    sequence_number = Column(Integer, nullable=False)
    event_type = Column(String(50), nullable=False)
    payload = Column(Text, nullable=False)  # JSON serialized data
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Sequence number must be unique per aggregate
    __table_args__ = (
        UniqueConstraint("aggregate_id", "sequence_number", name="uq_aggregate_seq"),
    )

# ==========================================
# READ MODELS: Projections Tables
# ==========================================
class UserRead(Base):
    __tablename__ = "users_read"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class FlightRead(Base):
    __tablename__ = "flights_read"

    id = Column(Integer, primary_key=True, index=True)
    flight_number = Column(String(20), nullable=False)
    origin = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    departure_time = Column(String(50), nullable=False)  # YYYY-MM-DD HH:MM
    price = Column(Float, nullable=False)
    available_seats = Column(Integer, nullable=False)
    image_url = Column(String(500), nullable=True)

class BookingRead(Base):
    __tablename__ = "bookings_read"

    id = Column(String(50), primary_key=True, index=True) # Booking UUID
    user_id = Column(Integer, nullable=False, index=True)
    flight_id = Column(Integer, nullable=False)
    passenger_name = Column(String(100), nullable=False)
    passport_number = Column(String(50), nullable=False)
    status = Column(String(20), default="Active")  # Active, Cancelled
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# Database helper function
def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
