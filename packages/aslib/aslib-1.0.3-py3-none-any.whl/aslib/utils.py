import base64
import bisect
import hashlib
import random
import socket
import uuid
import zlib

codec = "utf8"
characters = "01234567890abcdefghijklmnopqrstuvwxyz"

__all__ = [
    "random_string", "gets", "format_size",
    "uid", "md5", "md5file", "hostname",
    "compress", "decompress",
    "b64decode", "b64encode"
]


def random_string(length: int):
    return "".join([random.choice(characters) for _x in range(length)])


def gets(data: dict, path: str, default=None):
    path = path.strip()
    if path.find(".") > 0:
        prefix, suffix = path.split(".", 1)
        if prefix in data.keys():
            return gets(data[prefix], suffix, default)

    if path in data.keys():
        return data.get(path) or default

    return default


def format_size(size: int) -> str:
    d = [
        (1024 - 1, "KB"),
        (1024 ** 2 - 1, "MB"),
        (1024 ** 3 - 1, "GB"),
        (1024 ** 4 - 1, "TB"),
    ]
    s = [x[0] for x in d]
    index = bisect.bisect_left(s, size) - 1
    if index == -1:
        return f"{round(size, 2)}B"
    b, u = d[index]
    return f"{round(size / (b + 1), 2)}{u}"


def uid(keep_hyphen: bool = False):
    u = uuid.uuid4()
    if not keep_hyphen:
        return u.hex
    return str(u)


def md5(data):
    raw = data.encode(codec) if isinstance(data, str) else data
    m = hashlib.md5()
    m.update(raw)
    return m.hexdigest()


def md5file(path, chunk_size: int = 8192):
    m = hashlib.md5()
    with open(path, "rb") as fd:
        while True:
            chunk = fd.read(chunk_size)
            if not chunk:
                break
            m.update(chunk)
    return m.hexdigest()


def hostname():
    return socket.gethostname()


def compress(data: bytes):
    raw = data.encode(codec) if isinstance(data, str) else data
    return zlib.compress(raw)


def decompress(data: bytes):
    raw = data.encode(codec) if isinstance(data, str) else data
    return zlib.decompress(raw)


def b64encode(data, return_str=False):
    raw = data.encode(codec) if isinstance(data, str) else data
    r = base64.b64encode(raw)
    if return_str:
        return r.decode(codec)
    return r


def b64decode(data, return_str=False):
    raw = data.encode(codec) if isinstance(data, str) else data
    r = base64.b64decode(raw)
    if return_str:
        return r.decode(codec)
    return r
