import base64
import bisect
import hashlib
import random
import socket
import uuid
import zlib

codec = "utf8"


def random_string(length: int):
    characters = "01234567890abcdefghijklmnopqrstuvwxyz"
    return "".join([random.choice(characters) for _x in range(length)])


def gets(data: dict, key: str, default=None):
    if data and key in data.keys():
        return data[key]
    return default


def rgets(data: dict, path: str, default=None):
    if path.find(".") > 0:
        prefix, suffix = path.split(".", 1)
        if prefix in data.keys():
            return rgets(data[prefix], suffix, default)
    return gets(data, path, default)


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


def UID(keep_hyphen: bool = False):
    u = uuid.uuid4()
    if not keep_hyphen:
        return u.hex
    return str(u)


def MD5(data):
    raw = data.encode(codec) if isinstance(data, str) else data
    m = hashlib.md5()
    m.update(raw)
    return m.hexdigest()


def MD5File(path):
    m = hashlib.md5()
    chunk_size = 8192
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
