import abc
import signal
import time

from .signals import SignalWatcher

__all__ = ["IProgram"]


class IProgram:
    def __init__(self, *args, **kwargs) -> None:
        self._interrupted = False
        self._signal_watcher = SignalWatcher()
        self._signal_watcher.register()

        self.args = args
        self.kwargs = kwargs

    @property
    def interrupted(self):
        return self._interrupted

    def handle_error(self, error):
        pass

    def stop(self):
        pass

    def shutdown(self):
        self._interrupted = True

    def check_signal(self):
        sig = self._signal_watcher.get()
        if sig is None:
            return

        if sig in (signal.SIGINT, signal.SIGTERM):
            self._interrupted = True
            return

        sig_hup = getattr(signal, "SIGHUP", None)
        if sig_hup and sig_hup == sig:
            self._interrupted = True
            return

    def run_forever(self, *args, **kwargs):
        started, recovery = 0, 60
        while not self.interrupted:
            try:
                time.sleep(1)
            except Exception as err:
                self.handle_error(err)
                break

            self.check_signal()

            if int(time.time()) - started > recovery:
                try:
                    self.working()
                except Exception as err:
                    self.handle_error(err)
                finally:
                    started = int(time.time())
            self.check_signal()

    @abc.abstractmethod
    def working(self, *args, **kwargs):
        raise NotImplementedError
