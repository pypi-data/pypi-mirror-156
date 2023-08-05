import signal

__all__ = ["SignalWatcher"]

WATCH_SIGNALS = (
    "SIGINT",
    "SIGTERM",
    "SIGHUP",
    "SIGQUIT",
    "SIGUSER1",
)

SIGNAL_NAMES = {}
for k, v in signal.__dict__.items():
    startswith = getattr(k, "startswith", None)
    if startswith and startswith("SIG") and not startswith("SIG_"):
        SIGNAL_NAMES[v] = k


class SignalWatcher:
    def __init__(self):
        self._caches = []

    def register(self):
        for name in WATCH_SIGNALS:
            if hasattr(signal, name):
                sig = getattr(signal, name)
                if sig:
                    signal.signal(sig, self.receive)

    def receive(self, signal_number, frame):
        if signal_number not in self._caches:
            self._caches.append(signal_number)

    def name(self, signal_number):
        return SIGNAL_NAMES.get(signal_number) or f"Signal-{signal_number}"

    def get(self):
        if self._caches:
            return self._caches.pop(0)
        return None
