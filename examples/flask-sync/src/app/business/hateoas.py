from typing import Optional, Any

import urllib.parse

from pydantic import BaseModel


class Hyperlink(BaseModel):
    next: Optional[str]
    previous: Optional[str]
    current: Optional[str]
    about: Optional[str]
    self: Optional[str]

    class Config:
        title="Hyperlink"


def url(path: str, query_params: dict[str, Any], keys: set[str]) -> str:
    query_params = dict(
        (key, str(value))
        for key, value in query_params.items()
        if key in keys and value
    )
    url_parts = urllib.parse.urlparse(str(path))
    query = dict(urllib.parse.parse_qsl(url_parts.query))
    query.update(query_params)
    return url_parts._replace(query=urllib.parse.urlencode(query)).geturl()

