# Product Requirements Document (PRD)
## Flight Booking & Travel Assistant Desktop System

This document specifies the requirements, system design, data schemas, and API protocols for the Flight Booking & Travel Assistant. The application is developed as part of the Windows Systems Engineering curriculum, implementing modern software patterns in both Desktop frontend (PySide6, MVP, Microfrontends) and Backend layers (FastAPI, CQRS, Event Sourcing, API Gateway, Ollama RAG).

---

## 1. Objectives & Scope

The application assists users in searching flights, booking tickets, viewing travel destination weather forecasts, examining ticket price and order analytics, and asking travel policy or destination questions via an AI assistant.

### Key Features
1. **User Authentication**: Register and Login screens with secure password hashing.
2. **Flight Search Engine**: Query flights by origin, destination, and departure date.
3. **External Weather forecast**: Fetch real-time weather reports for destination cities (e.g. London, Paris, Tokyo, New York) using the Open-Meteo API.
4. **Data Entry & Reservation**: Complete a flight booking, input passenger names, verify passport info, and cancel bookings.
5. **Event Sourced Bookings**: Backend updates booking states by appending events to an Event Store database and projecting read-optimized views.
6. **Analytics Panel (QtCharts)**: Render price trends and reservation frequency using QtCharts.
7. **RAG-based AI Advisor**: Question-answering agent querying a local travel policy knowledge base using a local Ollama LLM container.

---

## 2. Architecture & Design Patterns

The architecture consists of a Desktop client communicating via an API Gateway with specialized backend domain modules:

```mermaid
graph TD
    Client[PySide6 Desktop App] -->|HTTP REST| Gateway[API Gateway / FastAPI Router]
    
    subgraph Frontend Architecture (MVP & Microfrontends)
        Client --> Shell[App Shell View / Presenter]
        Shell --> M_Auth[Auth Microfrontend]
        Shell --> M_Search[Search & Weather Microfrontend]
        Shell --> M_Booking[Booking Microfrontend]
        Shell --> M_Stats[Statistics QtCharts Microfrontend]
        Shell --> M_AI[AI Advisor Microfrontend]
    end

    subgraph Backend Services (CQRS & Event Sourcing)
        Gateway --> AuthSvc[Authentication Service]
        Gateway --> FlightSvc[Flight Query Service]
        Gateway --> BookingSvc[Booking Service (CQRS)]
        Gateway --> AISvc[AI Advisor (RAG + Ollama)]
        Gateway --> WeatherSvc[External Weather Service]
        
        BookingSvc -->|Command| EventStore[(SQLite/Postgres Event Store)]
        EventStore -->|Projection Update| ReadDB[(Read-Optimized Tables)]
        BookingSvc -->|Query| ReadDB
    end
```

### Architectural Details
- **Microfrontends**: The Desktop UI splits functionality into standalone modules, each registering its root widget inside a `QStackedWidget` in the App Shell. Coupling is minimized by utilizing a central `EventBus` for inter-module notifications.
- **Model-View-Presenter (MVP)**: Views are passive and contain layouts/controls only. User clicks/inputs emit signals to the Presenter. Presenters invoke Models/API client, fetch responses, and write updates back to the Views.
- **API Gateway**: A unified entry point in FastAPI routing client requests to individual business routers.
- **CQRS & Event Sourcing**: 
  - Write Model (Commands): Modifying actions append serializable events to the event log.
  - Read Model (Queries): Background projections query the event log, materializing static read-model tables for rapid retrieval.

---

## 3. Data Schemas

### 3.1 Event Store Schema (`events` table)
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER (PK) | Auto-incrementing identifier. |
| `aggregate_id` | TEXT | Identifier of the entity (e.g. Booking UUID). |
| `aggregate_type` | TEXT | Type of the entity (e.g. "Booking"). |
| `sequence_number` | INTEGER | Version number of the aggregate state. |
| `event_type` | TEXT | Type of event (e.g., `FlightBooked`, `BookingCancelled`). |
| `payload` | TEXT (JSON) | Event properties (passenger details, seats, cost). |
| `created_at` | DATETIME | Timestamp of event insertion. |

### 3.2 Read Model Schemas
- **`users_read`**: `id`, `username`, `password_hash`, `email`, `created_at`
- **`flights_read`**: `id`, `flight_number`, `origin`, `destination`, `departure_time`, `price`, `available_seats`, `image_url`
- **`bookings_read`**: `id` (booking UUID), `user_id`, `flight_id`, `passenger_name`, `passport_number`, `status` (`Active` / `Cancelled`), `created_at`

---

## 4. API Endpoints

### 4.1 Authentication Router
- `POST /api/auth/register`: Create user credentials.
- `POST /api/auth/login`: Validate user credentials and return a JWT Bearer token.
- `GET /api/auth/me`: Retrieve profile details for the authenticated user.

### 4.2 Flights Router
- `GET /api/flights/search`: Search flights by `origin`, `destination`, and `date`.
- `GET /api/flights/{id}`: Fetch single flight metadata.

### 4.3 Bookings Router (CQRS)
- `POST /api/bookings/book` [Command]: Append `FlightBooked` event, update read model, reserve ticket.
- `POST /api/bookings/{id}/cancel` [Command]: Append `BookingCancelled` event, set status to `Cancelled`.
- `GET /api/bookings/my-orders` [Query]: Fetch list of reservations for current user.
- `GET /api/bookings/statistics` [Query]: Retrieve aggregate statistics (monthly volume, average ticket prices) for charts.

### 4.4 AI Travel Advisor Router (RAG)
- `POST /api/ai/ask`: Send user query. Fetches context from `knowledge_base/travel_info.txt`, builds RAG prompt, queries Ollama, and returns response.

### 4.5 External Weather Router
- `GET /api/weather/forecast`: Fetches weather for a destination (maps destination to coordinates and calls Open-Meteo API).

---

## 5. Non-Functional Requirements

- **Local Execution**: The application backend and UI must run locally with minimal dependencies (SQLite, Python standard libraries).
- **Responsive Desktop GUI**: Main thread execution should remain unblocked during networking requests. Web queries and AI completions must run in background threads using `QThread` or `QRunnable`.
- **High-Fidelity Aesthetics**: Dark mode theme leveraging QSS styling, styled tables, elegant input fields, hover indicators, and animated load transitions.
- **Robust Error Handling**: Handle service offline states gracefully. If Ollama is not accessible, the backend returns clear diagnostic errors or falls back to a simulated heuristic rule-engine advisor.
