# AI Development Log

This log chronicles the key design choices, iterations, and problem-solving steps during the development and corrections phase of the WSE Flight Booking & Travel Assistant.

---

### Phase 1: Security Cleanup
- **Decision**: Refactored the hardcoded JWT secret in `config.py` and `.env.example` into a generic placeholder: `replace-with-a-long-random-secret`.
- **Mitigation**: Configured the backend gateway server to detect the default secret upon startup and output a strong warning log alert. Added notice in `README.md` warning developers to manually rotate credentials in production.

### Phase 2: Database Schema & Migrations
- **Decision**: Generated a complete initial Alembic migration version `001_initial.py` to match the SQLAlchemy Base metadata tables (`events`, `users_read`, `flights_read`, `bookings_read`).
- **Constraint**: Added the custom unique constraint:
  `UNIQUE (aggregate_type, aggregate_id, sequence_number)`
  directly on the Event Store table to support pessimistic validation checking.
- **Verification**: Discovered that if the SQLite DB is already auto-created by the app during startup, Alembic migration fails with "table events already exists". Tested the migration script successfully by setting an alternative database file (`fresh_test.db`).

### Phase 3: Event Sourcing & Concurrency
- **Transaction Atomicity**: Placed event storage and read model projection inside a single database transaction block. Implemented a specific testing mechanism inside `project_event` that triggers a `RuntimeError` if the passenger name is `"TriggerProjectionFailure"`. Asserted that `db.rollback()` cleanly removes both the stored event and projection read models.
- **Concurrency version conflict**: Added strict optimistic version checks using both `aggregate_type` and `aggregate_id`. Intercepted database commits and mapped `IntegrityError` (caused by duplicate event versions violating unique constraint) directly to `HTTP 409 Conflict`.
- **Projection Rebuilding**: Added the `capacity` field to `FlightRead` model and seeds. Re-programmed `rebuild_read_models` to dynamically reset available seats to `capacity` from database model values (eliminating hardcoded dictionaries) and replay events in deterministic order (`EventStore.id.asc()`).

### Phase 4: Desktop Responsive Threading
- **Worker Management**: Addressed PySide6 thread lifecycle safety and duplicate thread executions. Programmed a helper method `_start_worker` in presenters that:
  1. Stores references to running workers in an instance `_active_workers = set()` to prevent garbage collection and segmentation faults.
  2. Blocks launching identical worker types if they are already running.
  3. Connects the worker's `finished` signal to `worker.deleteLater` to clean up resources.
- **Event Bus Refactoring**: Discovered that `BookingPresenter` performed duplicate history requests: once locally, and once by triggering the global `bookings_updated` event which was also bound to history reloading. Removed local reload calls, allowing the event bus to coordinate single-path updates.
- **UI Reset**: Connected selection changes and cancellation outcomes to automatically restore button states and loading notifications.

### Phase 5: Fallback & API Cleanups
- **MVP Refactoring**: Refactored the empty stub class `SearchModel` in `search/presenter.py` into a data access layer wrapper for flight searching and detail lookups.
- **Fake Weather Removal**: Replaced mock offline weather responses with an honest error payload: `{"detail": "Weather service unavailable"}`. Verified that the view successfully handles and displays this error without default mock values.
