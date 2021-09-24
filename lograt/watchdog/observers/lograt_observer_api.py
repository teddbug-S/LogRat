from watchdog.observers import Observer


class LogRatObserverAPI(Observer):
    """
    LogRatObserverAPI directly subclasses watchdog.observers.Observer
    to override dispatch_events method to dispatch each event with the
    name of the thread triggering that change.
    """
    def __init__(self):
        super().__init__()

    def dispatch_events(self, event_queue, timeout):
        event, watch = event_queue.get(block=True, timeout=timeout)

        with self._lock:
            # To allow unschedule/stop and safe removal of event handlers
            # within event handlers itself, check if the handler is still
            # registered after every dispatch.
            for handler in list(self._handlers.get(watch, [])):
                if handler in self._handlers.get(watch, []):
                    handler.dispatch(event, self.name)
        event_queue.task_done()
