# WSE Architecture Design Document

This document describes the architectural design of the WSE Flight Booking & Travel Assistant application.

---

## 1. System Overview

The system is split into a **PySide6 Desktop Client Application (Frontend)** and a **FastAPI Gateway Application (Backend)**. Communication is done asynchronously over standard HTTP JSON APIs.

```mermaid
graph TD
    subgraph Frontend (PySide6 Desktop Application)
        Shell[AppShellView]
        AuthPresenter[AuthPresenter]
        SearchPresenter[SearchPresenter]
        BookingPresenter[BookingPresenter]
        StatsPresenter[StatsPresenter]
        DetailsPresenter[DetailsPresenter]
        AIPresenter[AIAdvisorPresenter]
    end

    subgraph Backend (FastAPI Web Server Gateway)
        API[API Gateway Router]
        AuthSvc[Auth Service]
        FlightSvc[Flight Service]
        BookingSvc[Booking Service & CQRS]
        WeatherSvc[External Weather Service]
        AISvc[AI Advisor RAG Service]
    end

    Shell --> AuthPresenter
    Shell --> SearchPresenter
    Shell --> BookingPresenter
    Shell --> StatsPresenter
    Shell --> DetailsPresenter
    Shell --> AIPresenter

    AuthPresenter --> AuthSvc
    SearchPresenter --> FlightSvc
    BookingPresenter --> BookingSvc
    DetailsPresenter --> WeatherSvc
    AIPresenter --> AISvc

    subgraph Database Subsystem
        DB[(SQLite / PostgreSQL)]
    end

    BookingSvc --> DB
    FlightSvc --> DB
    AuthSvc --> DB
    
    subgraph External Systems
        OpenMeteo[Open-Meteo Weather API]
        Ollama[Ollama llama3.2:1b Container]
    end

    WeatherSvc --> OpenMeteo
    AISvc --> Ollama
```

---

## 2. CQRS & Event Sourcing (Bookings Domain)

The Bookings module separates write operations (Commands) from read operations (Queries) using Event Sourcing:

1. **Commands (Write Model)**:
   - When a booking is submitted (`/bookings/book`) or cancelled (`/bookings/.../cancel`), the system creates a domain event (e.g. `FlightBooked`, `BookingCancelled`).
   - The event is appended to the `events` table (Event Store) in a transaction.
   - The event sequence number must be unique per aggregate (`aggregate_type`, `aggregate_id`, `sequence_number`).
   - Any concurrent write attempting to insert a duplicate sequence version fails due to the database unique constraint, raising an `IntegrityError` which is caught and returned as an HTTP `409 Conflict`.

2. **Projections (Read Model)**:
   - Inside the same transaction, the event is immediately passed to the projection engine (`project_event`).
   - The projection engine updates the Read tables: `bookings_read` (inserts/cancels reservations) and `flights_read` (adjusts `available_seats`).
   - If projection fails (e.g. invalid state, validation checks), the entire transaction rolls back, ensuring no event is written and no projection is modified.

3. **Projection Rebuilding**:
   - Rebuilding projection state (`rebuild_read_models`) clears `bookings_read`, resets `available_seats` of all flights back to their stored database `capacity`, and replays all events from `EventStore` in deterministic order (`EventStore.id.asc()`), guaranteeing a repeatable and identical read model state.

---

## 3. PySide6 Threading Architecture

To maintain a fully responsive desktop GUI, all synchronous API calls to the FastAPI backend are delegated to background threads using subclassed `QThread` workers:

- Presenters use `RequestWorker` (and specialized `WeatherWorker` or `QueryWorker`) to perform the network requests.
- Each presenter maintains an `_active_workers` set to hold python references to running worker threads, preventing premature garbage collection.
- Presenters check if a worker is already running before starting it, preventing concurrent duplicate background requests.
- Workers connect their `finished` signal to `worker.deleteLater` to ensure C++ objects are cleaned up properly upon exit, and discard themselves from the presenter's active set.
- Event Bus subscriptions update separate presenters globally (e.g. when a booking updates, statistics and booking history reload safely without duplicate API calls).

---

## 4. AI Advisor RAG Service

The RAG Travel Advisor handles user queries based strictly on stored travel documents:

1. **Context Indexing**: During server startup, `knowledge_base/travel_info.txt` is parsed into sections and indexed using `SentenceTransformer("all-MiniLM-L6-v2")` to generate vector embeddings.
2. **Semantic Retrieval**: A cosine similarity lookup retrieves the top matching context blocks for a query. If transformers are unavailable, keyword search is utilized as a fallback.
3. **Inference (Ollama)**: The retrieved context and a strict system prompt constraint are sent to a local Ollama service (`llama3.2:1b`) to generate the final advice. If Ollama is offline, the system gracefully prints matching sections directly as a fallback.
