from typing import Optional, Type, Literal
from dataclasses import dataclass

from pydantic import BaseModel
from pydantic.schema import schema

from apispec import APISpec

PARAMETER_TYPE = Literal['int', 'uuid']


@dataclass(frozen=True)
class Parameter:
    description: str
    schema: PARAMETER_TYPE
    name: str


@dataclass(frozen=True)
class Response:
    description: str
    schema: Type[BaseModel]
    status: int = 200


@dataclass(frozen=True)
class Body:
    schema: Type[BaseModel]


class MethodProxy:
    def __init__(self, definition_holder, method_view):
        self.definition_holder = definition_holder
        self.method_view = method_view

    def __getattr__(self, item):
        return getattr(self.definition_holder, item)

    def __call__(self, *args, **kwargs):
        return self.definition_holder(self.method_view, *args, **kwargs)


class AbstractDefinitionHolder:
    def __init__(self, definition, handler):
        self.definition = definition
        self.handler = handler

    def dispose(self):
        del self.definition

    def __get__(self, instance, owner):
        return MethodProxy(self, instance)


@dataclass(frozen=True)
class DefinitionSchema:
    summary: str
    response: Response
    tag: Optional[str] = None
    parameter: Optional[list[Parameter]] = None
    body: Optional[Body] = None

    def __call__(self, f): ...


@dataclass(frozen=True)
class Definition(DefinitionSchema):
    class DefinitionHolder(AbstractDefinitionHolder):
        def __call__(self, instance, *args, **kwargs):
            return self.handler(instance, *args, **kwargs)

    def __call__(self, f):
        return Definition.DefinitionHolder(self, f)


@dataclass(frozen=True)
class AsyncDefinition(DefinitionSchema):
    class DefinitionHolder(AbstractDefinitionHolder):
        async def __call__(self, instance, *args, **kwargs):
            return await self.handler(instance, *args, **kwargs)

    def __call__(self, f):
        return Definition.DefinitionHolder(self, f)


def specification_from_endpoints(endpoints):
    definitions = list(
        getattr(endpoint, operation_name).definition
        for endpoint in endpoints
        for operation_name in ('get', 'post')
        if hasattr(endpoint, operation_name)
    )

    all_schemas = set()
    for definition in definitions:
        if definition.body is not None:
            all_schemas.add(definition.body.schema)
        all_schemas.add(definition.response.schema)

    schemas = schema(all_schemas, ref_prefix="#/components/schemas/")['definitions']
    schemas_reverse_identifiers = dict(
        (schema_definition['title'], schema_identifier)
        for schema_identifier, schema_definition in schemas.items()
    )
    assert len(schemas_reverse_identifiers) == len(schemas), "Non unique schema titles"

    specification = APISpec(
        title="My dummy API (Change this title)",
        version="1.0.0",
        openapi_version="3.0.3"
    )
    for identifier, schema_definition in schemas.items():
        specification.components.schema(identifier, schema_definition)

    def type_of_parameter(param_type: PARAMETER_TYPE):
        if param_type == 'int':
            return dict(type='integer')
        elif param_type == 'uuid':
            return dict(type='string', format='uuid')

    for endpoint in endpoints:
        route, args = endpoint.route(_split=True)

        operations = dict()
        for operation_name in ('get', 'post'):
            if not hasattr(endpoint, operation_name):
                continue
            definition = getattr(endpoint, operation_name).definition
            if definition.body:
                request_body = dict(
                    required=True,
                    content={
                        'application/json': {
                            'schema': schemas_reverse_identifiers[definition.body.schema.Config.title]
                        }
                    }
                )
            else:
                request_body = None
            parameters = list(
                {
                    'in': 'query',
                    'name': def_param.name,
                    'description': def_param.description,
                    'schema': type_of_parameter(def_param.schema)
                }
                for def_param in (definition.parameter or list())
                if def_param
            )
            response = definition.response
            operations[operation_name] = {
                'summary': definition.summary,
                'responses': {
                    response.status: {
                        'description': response.description,
                        'content': {
                            'application/json': {
                                'schema': schemas_reverse_identifiers[
                                response.schema.Config.title]
                            }
                        }
                    }
                }
            } | (
                dict(parameters=parameters) if parameters else dict()
            ) | (
                dict(requestBody=request_body) if request_body else dict()
            )

            getattr(endpoint, operation_name).dispose()

        specification.path(
            path=route,
            operations=operations,
            parameters=list(
                {
                    'in': 'path',
                    'name': args_key,
                    'schema': type_of_parameter(args_type),
                    'required': True
                }
                for args_key, args_type in args.items()
            ) if args else None
        )

    return specification
