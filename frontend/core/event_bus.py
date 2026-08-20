class EventBus:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance.listeners = {}
        return cls._instance

    def subscribe(self, event_type: str, callback):
        """Subscribe a callback to a specific event type."""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback):
        """Unsubscribe a callback from an event type."""
        if event_type in self.listeners:
            try:
                self.listeners[event_type].remove(callback)
            except ValueError:
                pass

    def emit(self, event_type: str, *args, **kwargs):
        """Emit an event, invoking all registered callbacks with arguments."""
        if event_type in self.listeners:
            # Iterate over a copy of listeners list to allow callbacks to unsubscribe during emission
            for callback in list(self.listeners[event_type]):
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    import logging
                    logging.getLogger(__name__).error(
                        f"Error in EventBus listener for event '{event_type}': {e}"
                    )

# Global singleton event bus
event_bus = EventBus()
