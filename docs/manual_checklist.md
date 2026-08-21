# WSE Manual Verification Checklist

Use this checklist to manually verify all user-facing flows and system behaviors of the desktop application.

---

## 1. Environment & Setup

- [ ] **Database Migration**:
  - Delete `travel_assistant.db`.
  - Run `alembic upgrade head`.
  - Check that a new `travel_assistant.db` database is created.
  - Run the FastAPI backend (`uvicorn backend.app.main:app --port 8080`) and verify that flight seed values are populated correctly upon startup.

- [ ] **Docker Ollama Setup**:
  - Run `docker compose up -d`.
  - Run `docker exec -it ollama ollama pull llama3.2:1b`.
  - In a browser, check `http://localhost:11434` returns "Ollama is running".
  - Verify container status through backend health `/api/ai/status`.

---

## 2. User Authentication Flows

- [ ] **Registration**:
  - Open PySide6 frontend.
  - Go to the register tab.
  - Enter a username and email, plus a short password (< 4 characters) -> Verify error message displays correctly.
  - Enter a valid username, email, and password -> Click register.
  - Verify that the app transitions to the login tab and pre-fills the registered username.

- [ ] **Login**:
  - Enter incorrect credentials -> Verify "Incorrect username or password" displays.
  - Enter correct credentials -> Verify successful login, transition to search tab, and update of user welcome status.

---

## 3. Search & Booking Flows

- [ ] **Flight Search**:
  - Perform search with default values -> Check flights are returned.
  - Search using origin "Tel Aviv" and date "2026-08-25" -> Verify "LY-101" is shown.
  - Click Search multiple times rapidly -> Verify the search button is disabled during load and does not spawn duplicate workers.

- [ ] **Flight Details & Weather**:
  - Click "View Details" on a flight to Paris.
  - Verify flight details are shown.
  - Verify weather updates in the background thread (fetches temperature, conditions, and windspeed from Open-Meteo).
  - Select Rome, London, New York -> Verify weather loads.
  - *To test weather offline*: Disable network adapter -> Select details again -> Verify display says "Error loading weather" with "Weather service unavailable" and no mock values are displayed.

- [ ] **Booking Creation**:
  - Click "Book This Flight Now" from details tab -> Verify tab transitions to Booking with flight details pre-filled.
  - Enter passenger name containing numbers -> Verify validation error.
  - Enter valid passenger name and passport -> Click Confirm.
  - Verify confirmation success message, form clear, and booking history update.

- [ ] **Booking Cancellation**:
  - Select an active booking in the reservation history table -> Click "Cancel Selected Ticket".
  - Verify cancellation progress displays, status changes to "Cancelled" in red, and seats are incremented back on the flights.
  - *To test failed cancellation*: Attempt to cancel a booking while backend is offline -> Verify Cancel button is restored and re-enabled, and does not remain permanently disabled.
