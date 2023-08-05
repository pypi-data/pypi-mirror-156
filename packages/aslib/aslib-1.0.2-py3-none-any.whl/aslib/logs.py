import os
import sys
import threading

from loguru._logger import Core, Logger

_locker = threading.Lock()
_logges = {}

LOG_FORMAT = "{level} {time:YYYY/MM/DD HH:mm:ss.SS} {module}[{line}]: {message}"
TRACE = "TRACE"
DEBUG = "DEBUG"
INFO = "INFO"
WARNING = "WARNING"
ERROR = "ERROR"
CRITICAL = "CRITICAL"


def getLogger(module: str, level=TRACE, backtrace=False, echo=False):
    with _locker:
        if module in _logges.keys():
            return _logges[module]

        logger = Logger(
            core=Core(),
            exception=None,
            depth=0,
            record=False,
            lazy=False,
            colors=False,
            raw=False,
            capture=True,
            patcher=None,
            extra={},
        )
        logger.remove()
        if level == DEBUG:
            echo = True

        if level == TRACE:
            backtrace = True
            echo = True

        if echo:
            logger.add(sys.stdout, level=INFO, format=LOG_FORMAT, backtrace=True)

        else:
            log_dirs = os.path.join(os.getcwd(), "logs")
            if not os.path.exists(log_dirs):
                os.makedirs(log_dirs)
            abspath = os.path.join(log_dirs, module + "_{time:YYYY-MM-DD}.log")
            logger.add(
                abspath,
                level=level,
                format=LOG_FORMAT,
                backtrace=backtrace,
                enqueue=True,
                encoding="utf8",
                rotation="daily",
            )

        _logges[module] = logger
        return logger
