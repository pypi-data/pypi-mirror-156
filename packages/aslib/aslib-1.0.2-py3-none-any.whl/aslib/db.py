import contextlib

from sqlalchemy import Column, Index
from sqlalchemy import Integer, String, Text, DateTime, BLOB
from sqlalchemy import create_engine as sqla_create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool, NullPool, StaticPool

__all__ = ["Table", "PoolImpl", "Database", "Column", "Index", "Integer", "String", "Text", "BLOB", "DateTime"]

Table = declarative_base()


class PoolImpl:
    null = NullPool
    queue = QueuePool
    static = StaticPool


class Database(object):
    def __init__(self, opt, **kwargs) -> None:
        self.opt = opt
        self.engine = None
        self.session_maker = None

        driver = kwargs.pop("driver") or "mysql+pymysql"
        charset = kwargs.pop("charset") or "utf8"
        pool_class = kwargs.pop("pool_class") or PoolImpl.queue
        pool_size = kwargs.pop("pool_size") or 1
        pool_pre_ping = kwargs.pop("pool_pre_ping")
        echo = kwargs.pop("echo")

        query = {"charset": charset}
        url = URL.create(
            driver,
            self.opt.user,
            self.opt.password,
            self.opt.host,
            self.opt.port,
            self.opt.database,
            query
        )
        engine_params = {
            "poolclass":     pool_class,
            "pool_size":     pool_size,
            "pool_pre_ping": pool_pre_ping,
            "echo":          echo,
        }
        self.engine = sqla_create_engine(url, **engine_params)
        self.session_maker = sessionmaker(bind=self.engine, autoflush=True)
        Table.metadata.create_all(self.engine)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.engine:
            self.engine.dispose()

    @contextlib.contextmanager
    def session(self):
        session = self.session_maker()
        try:
            yield session
            session.commit()
        finally:
            session.close()
