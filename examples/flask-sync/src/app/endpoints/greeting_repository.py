from uuid import UUID
from typing import Iterable, Optional

from flask.views import MethodView

from pydantic import BaseModel

from sqlalchemy import select, insert, func, Engine as DbEngine

from app.business.table_defs import GreetingTable, new_uuid, DatabaseGateway
from app.business.pagination import Paginated
from app.business.hateoas import Hyperlink, url
import app.business.openapi as openapi

from app.endpoints.greeting import GreetingDetail


class CreationData(BaseModel):
    message: Optional[str]

    class Config:
        title="GreetingCreationData"


class Summary(BaseModel):
    message: Optional[str]
    links: Hyperlink

    class Config:
        title="GreetingViewItemSummary"


class View(BaseModel):
    page: int
    page_size: int
    total_count: int
    items: list[Summary]
    links: Hyperlink

    class Config:
        title="GreetingView"


class Engine:
    @classmethod
    def route(cls, *args, **kwargs): ...

    def __init__(self, engine: DbEngine, greeting_table: GreetingTable, entity_link_forge):
        self.engine = engine
        self.greeting_table = greeting_table
        self.entity_link_forge = entity_link_forge

    def do_post(self, creation_data: CreationData) -> View:
        with self.engine.connect() as connection:
            with connection.begin():
                greeting_uuid = self._insert_in_db(creation_data.message, connection)

        view = self.do_get(Paginated(page_size=3))
        if greeting_uuid:
            view.links.current = self.entity_link_forge(greeting_uuid=greeting_uuid)
        return view

    def do_get(self, paginated: Paginated) -> View:
        with self.engine.connect() as connection:
            connection.execution_options(isolation_level='AUTOCOMMIT')
            records = self._fetch_greetings_from_db(paginated, connection)
            total_count = self._fetch_total_greeting_count_from_db(connection)

        previous_paginated = paginated.previous(total_count=total_count)
        next_paginated = paginated.next(total_count=total_count)

        return View(
            page=paginated.page,
            page_size=paginated.page_size,
            total_count=total_count,
            items=list(records),
            links=Hyperlink(
                previous=self.route(
                    page=previous_paginated.page,
                    page_size=previous_paginated.page_size
                ) if previous_paginated else None,
                next=self.route(
                    page=next_paginated.page,
                    page_size=next_paginated.page_size
                ) if next_paginated else None,
                self=self.route(
                    page=paginated.page,
                    page_size=paginated.page_size
                )
            )
        )

    def _fetch_total_greeting_count_from_db(self, connection) -> int:
        count_query = select(func.count()).select_from(self.greeting_table)
        with connection.execute(count_query) as result:
            number, *_ = result.fetchone() or (0,)
            return number

    def _fetch_greetings_from_db(self, paginated: Paginated, connection) -> Iterable[Summary]:
        query = select(
            self.greeting_table.columns.uuid,
            self.greeting_table.columns.text
        ).select_from(self.greeting_table).slice(
            start=paginated.start, stop=paginated.stop
        )
        with connection.execute(query) as result:
            records = result.fetchall()
        return (Summary(
            message=record[1],
            links=Hyperlink(about=self.entity_link_forge(greeting_uuid=record[0]))
        ) for record in records)

    def _insert_in_db(self, text: Optional[str], connection) -> UUID:
        model_uuid = new_uuid()
        connection.execute(insert(self.greeting_table).values(
            text=text,
            uuid=model_uuid
        ))
        return model_uuid


class Greeting(MethodView, Engine):
    @classmethod
    def route(cls, _split=False, **kwargs):
        if _split:
            return '/greeting', dict()
        else:
            return url('/greeting', kwargs, {'page', 'page_size'})

    def __init__(self, *args, **kwargs):
        MethodView.__init__(self)
        db_gateway = DatabaseGateway.instance()
        Engine.__init__(self,
                        engine=db_gateway.engine,
                        greeting_table=db_gateway.greeting_table,
                        entity_link_forge=GreetingDetail.route)

    @openapi.TypeAggressiveDefinition(
        summary="Get a Greeting",
        tag="greet",
        parameter=[
            openapi.Parameter(
                name="page",
                schema=int,
                description="Page to fetch in the pagination"
            ),
            openapi.Parameter(
                name="page_size",
                schema=int,
                description="Expected page size"
            )
        ],
        response=openapi.Response(
            status=200,
            description="Paginated view of greetings",
            schema=View
        )
    )
    def get(self, page: Optional[int], page_size: Optional[int]) -> View:
        pagination = Paginated(
            page=page or 1,
            page_size=page_size or 3
        )
        return self.do_get(pagination)

    @openapi.TypeAggressiveDefinition(
        summary="Create a Greeting",
        tag="greet",
        response=openapi.Response(
            status=201,
            description="Create a greeting and never look back",
            schema=View
        ),
        body=openapi.Body(schema=CreationData)
    )
    def post(self, data: CreationData) -> View:
        return self.do_post(data)
