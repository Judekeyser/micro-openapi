from uuid import UUID
from typing import Optional

from flask import abort
from flask.views import MethodView

from pydantic import BaseModel

from sqlalchemy import select, Engine as DbEngine

from app.business.table_defs import GreetingTable, DatabaseGateway
import microapi.extension as openapi


class Summary(BaseModel):
    message: Optional[str]

    class Config:
        title="GreetingEntitySummary"


class Engine:
    @classmethod
    def route(cls, *args, **kwargs): ...

    def __init__(self, engine: DbEngine, greeting_table: GreetingTable):
        self.engine = engine
        self.greeting_table = greeting_table

    def do_get(self, greeting_uuid: UUID) -> Optional[Summary]:
        with self.engine.connect() as connection:
            connection.execution_options(isolation_level='AUTOCOMMIT')
            summary = self._fetch_greeting_from_db(greeting_uuid, connection)

        if not summary:
            return None
        else:
            return summary

    def _fetch_greeting_from_db(self, greeting_uuid: UUID, connection) -> Optional[Summary]:
        query = select(
            self.greeting_table.columns.uuid,
            self.greeting_table.columns.text
        ).where(self.greeting_table.columns.uuid == greeting_uuid).limit(1).select_from(self.greeting_table)

        with connection.execute(query) as result:
            record = result.fetchone()

        if not record:
            return None
        else:
            return Summary(message=record[1])


class GreetingDetail(MethodView, Engine):
    @classmethod
    def route(cls, greeting_uuid: str=None, _split=False, **kwargs):
        if _split:
            return '/detail/{greeting_uuid}', dict(greeting_uuid='uuid')
        else:
            generic, args = cls.route(_split=True)
            if greeting_uuid:
                return generic.format(greeting_uuid=greeting_uuid)
            else:
                new_args = dict(
                    (key, '<' f'{key}' '>')
                    for key, _type in args.items()
                )
                return generic.format(**new_args)

    def __init__(self, *args, **kwargs):
        MethodView.__init__(self)
        db_gateway = DatabaseGateway.instance()
        Engine.__init__(self,
                        engine=db_gateway.engine,
                        greeting_table=db_gateway.greeting_table)

    @openapi.TypeAggressiveDefinition(
        summary="Get a Greeting",
        tag="greet",
        response=openapi.Response(
            status=200,
            description="Get a Greeting object from very deep dark places",
            schema=Summary
        )
    )
    def get(self, greeting_uuid: str) -> Summary:
        summary = self.do_get(UUID(greeting_uuid))
        if not summary:
            abort(404)
        else:
            return summary
