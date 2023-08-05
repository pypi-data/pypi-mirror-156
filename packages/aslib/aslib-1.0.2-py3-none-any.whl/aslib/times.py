import datetime
import math


def now(offset_hours: int = 0) -> datetime.datetime:
    n = datetime.datetime.utcnow()
    if offset_hours > 0:
        delta = datetime.timedelta(hours=offset_hours)
        n += delta
    return n


def str_now(fmt="%Y-%m-%d-%H-%M-%S", offset_hours: int = 0) -> str:
    n = now(offset_hours)
    return n.strftime(fmt).strip()


def timestamp(length: int = 10, offset_hours: int = 0) -> int:
    bit = length - 10 if length > 10 else 0
    p = math.pow(10, bit)
    n = now(offset_hours)
    return int(n.timestamp() * p)


def ts_to_date(ts, fmt="%Y-%m-%d %H:%M:%S"):
    ts = int(ts)
    d = datetime.datetime.utcfromtimestamp(ts)
    return d.strftime(fmt)
