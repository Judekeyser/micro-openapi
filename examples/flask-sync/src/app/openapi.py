from typing import Optional, Type, Union
from dataclasses import dataclass
from uuid import UUID

from microapi.extension import Definition, PARAMETER_TYPE


@dataclass(frozen=True)
class TypeAggressiveDefinition(Definition):
    """This is an example of type agressive extension."""
    def __call__(self, f):
        from flask import request

        body = self.body
        parameter = self.parameter

        def kernel(instance, *args, **kwargs):
            if body:
                kwargs |= dict(data=body.schema.parse_obj(request.get_json()))
            if parameter:
                def extract_param_from_request(value, expected_type: PARAMETER_TYPE) -> Optional[Union[int, UUID]]:
                    if value is None:
                        return None
                    elif expected_type == int:
                        return int(value)
                    elif expected_type == UUID:
                        return UUID(value)

                kwargs |= dict(
                    (param.name, extract_param_from_request(request.args.get(param.name, None), param.schema))
                    for param in parameter
                    if param
                )

            result = f(instance, *args, **kwargs)
            return result.json(exclude_none=True)

        return Definition.__call__(self, kernel)

