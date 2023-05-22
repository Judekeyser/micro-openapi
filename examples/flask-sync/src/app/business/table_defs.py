import os
from uuid import UUID, uuid1
from typing import NewType, cast
from dataclasses import dataclass

from sqlalchemy import Table, MetaData, Column, Engine, create_engine, Integer, Uuid, String

GreetingTable = NewType('GreetingTable', Table)


def _create_greeting_table(meta: MetaData) -> GreetingTable:
    return GreetingTable(Table(
        "greeting", meta,
        Column("id", Integer, primary_key=True, unique=True, nullable=False, autoincrement=True),
        Column("uuid", Uuid, unique=True, nullable=False),
        Column("text", String)
    ))


def connection_string_from_env(dialect: str = "postgresql+psycopg") -> str:
    return (
        "{dialect}://"
        "{username}:{password}"
        "@{host}/{database}"
    ).format(
        dialect=dialect,
        username=os.getenv("db_username"),
        password=os.getenv("db_password"),
        host=os.getenv("db_host"),
        database=os.getenv("db_database")
    )


@dataclass
class DatabaseGateway:
    engine: Engine
    greeting_table: GreetingTable

    @staticmethod
    def instance(): ...

    @staticmethod
    def create(sync_connection_string, **kwargs) -> 'DatabaseGateway':
        meta = MetaData()
        engine = create_engine(sync_connection_string, echo=True)
        try:
            gateway = DatabaseGateway(
                greeting_table=_create_greeting_table(meta),
                engine=engine
            )
            meta.create_all(engine)
            DatabaseGateway.instance = lambda: gateway
            return gateway
        finally:
            pass#engine.dispose(close=True)

    @staticmethod
    def from_request(request):
        return cast(DatabaseGateway, request.app.ctx.db_gateway)


def new_uuid() -> UUID:
    return uuid1()
