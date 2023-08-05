import errno
import os
import shutil
import stat

DEFAULT_MODE = stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO

__all__ = ["scan_dirs", "parent", "joins", "mkdir", "remove", "touch", "read_file", "iter_file", "write_file"]


def scan_dirs(directory: str, limit_count: int = 0, limit_size: int = 0, exclude_ext: list = None):
    if not exclude_ext:
        exclude_ext = [".tmp", ".temp", ".TMP", ".TEMP"]
    paths = set()
    for root, _, names in os.walk(directory):
        for name in names:
            _, ext = os.path.splitext(name)
            abspath = os.path.join(root, name)
            file_size = os.path.getsize(abspath)

            if exclude_ext and ext in exclude_ext:
                continue
            if 0 < limit_size < file_size:
                continue
            if 0 < limit_count < len(paths):
                return list(paths)
            paths.add(abspath)
    return list(paths)


def parent(path):
    return os.path.dirname(path)


def joins(*args):
    return os.path.join(*args)


def mkdir(path, mode=DEFAULT_MODE):
    try:
        os.makedirs(path, mode)
    except OSError as err:
        if err.errno == errno.EEXIST:
            if not os.path.isdir(path):
                raise
        else:
            raise
    finally:
        return path


def remove(path: str):
    if os.path.isfile(path):
        try:
            os.remove(path)
        except OSError as err:
            raise RuntimeError(err)
    elif os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
    else:
        raise RuntimeError(f"Unknown type, {path}")


def touch(path: str):
    mkdir(parent(path))
    with open(path, "w") as fd:
        fd.write("")


def read_file(path: str, mode: str = "r"):
    with open(path, mode) as fd:
        return fd.read()


def iter_file(path: str, mode: str = "r"):
    for line in open(path, mode):
        yield line


def write_file(path: str, raw):
    mode = "w" if isinstance(raw, str) else "wb"
    with open(path, mode) as fd:
        fd.write(raw)
