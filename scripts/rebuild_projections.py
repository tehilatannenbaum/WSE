import sys
import os

# Add root folder to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.database import SessionLocal
from backend.app.bookings.service import rebuild_read_models

def main():
    print("==========================================")
    print("REBUILDING EVENT SOURCING PROJECTIONS")
    print("==========================================")
    
    db = SessionLocal()
    try:
        rebuild_read_models(db)
        print("[OK] Booking read models and flight seat counts replayed successfully!")
    except Exception as e:
        print(f"[FAIL] Projection rebuilding failed: {e}")
        sys.exit(1)
    finally:
        db.close()
    print("==========================================")

if __name__ == "__main__":
    main()
