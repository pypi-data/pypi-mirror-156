import configparser
import json
import os

import yaml


def load_ini(file_path: str) -> dict:
    parser = configparser.SafeConfigParser()
    if not parser.read(file_path):
        raise RuntimeError(f"No such file: {file_path}")

    configures = {}
    for section in parser.sections():
        configures[section] = {}
        for option in parser.options(section=section):
            configures[section][option] = parser.get(section, option)
    return configures


def load_yaml(file_path: str) -> dict:
    with open(file_path, "r") as fd:
        return yaml.load(fd, Loader=yaml.FullLoader)


def load_json(file_path: str) -> dict:
    with open(file_path, "r") as fd:
        return json.load(fd)


class Config:
    def __init__(self, path) -> None:
        filename = os.path.basename(path)
        _, suffix = os.path.splitext(filename)
        invoker = {
            ".ini":  load_ini,
            ".yaml": load_yaml,
            ".json": load_json
        }
        self.configs = invoker[suffix](path)

    def __gets(self, container: dict, path: str, default=None):
        path = path.strip()
        if path.find(".") > 0:
            prefix, suffix = path.split(".", 1)
            if prefix in container.keys():
                return self.__gets(container[prefix], suffix, default)

        if path in container.keys():
            return container[path]

        return default

    def get(self, path: str, default=None):
        return self.__gets(self.configs, path, default)
