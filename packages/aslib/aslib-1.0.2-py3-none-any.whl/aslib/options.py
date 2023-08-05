from dataclasses import dataclass, field


@dataclass(repr=True)
class DBOption:
    host: str
    port: int
    user: str
    password: str = field(repr=False)
    database: str
    charset: str = field(default="utf8mb4")


@dataclass(repr=True)
class MQOption:
    host: str
    port: int
    user: str
    password: str = field(repr=False)
    namespace: str
    exchange: str
    queue: str
    routing_key: str
    exchange_type: str = field(default="topic")
