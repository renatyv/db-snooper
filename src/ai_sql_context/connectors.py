from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


@dataclass(frozen=True)
class ConnectionConfig:
    dialect: str
    host: str
    port: int
    database: str
    user: str
    password: str


def create_db_engine(config: ConnectionConfig) -> Engine:
    dialect = config.dialect.lower()
    if dialect in {"mysql", "mariadb"}:
        driver = "mysql+pymysql"
    else:
        raise ValueError(f"Unsupported dialect for this version: {config.dialect}")

    user = quote_plus(config.user)
    password = quote_plus(config.password)
    host = config.host
    database = quote_plus(config.database)
    url = f"{driver}://{user}:{password}@{host}:{config.port}/{database}?charset=utf8mb4"
    return create_engine(url, future=True)
