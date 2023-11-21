from __future__ import annotations

import json
from typing import Any, TypeVar, List

try:
    from rich import print  # noqa
except:
    pass

from httpx import Response

from pydantic import BaseModel, TypeAdapter


class DirectusResponse:
    T = TypeVar("T", bound=BaseModel)

    def __init__(self, response: Response, query: dict = None, collection: Any = None):
        self.response: Response = response
        self.query: dict = query
        self.collection: Any = collection

        try:
            self.json: dict = response.json()
            if self.is_error:
                raise DirectusException(self)
        except json.decoder.JSONDecodeError:
            self.json = {}

    def _parse_item_as_dict(self) -> dict:
        if isinstance(self.json['data'], list):
            return self.json['data'][0]
        return self.json['data']

    def _parse_item_as_object(self, collection: T) -> T:
        return collection(**self._parse_item_as_dict())

    def _parse_items_as_dict(self) -> list[dict]:
        if isinstance(self.json['data'], list):
            return self.json['data']
        return [self.json['data']]

    def _parse_items_as_objects(self, collection: T) -> List[T]:
        items_data = self._parse_items_as_dict()
        return TypeAdapter(List[collection]).validate_python(items_data)

    @property
    def item(self) -> dict[Any, Any] | None | Any:  # noqa
        if 'data' not in self.json or self.json['data'] in [None, [], {}]:
            return None
        if self.collection:
            return self._parse_item_as_object(self.collection)
        return self._parse_item_as_dict()

    def item_as(self, collection: T) -> T | None:  # noqa
        item_data = self._parse_item_as_dict()
        return None if item_data is None else collection(**item_data)

    def item_as_dict(self) -> dict | None:  # noqa
        if "data" not in self.json or self.json['data'] in [None, [], {}]:
            return None
        return self._parse_item_as_dict()

    @property
    def items(self) -> list[dict[Any, Any]] | None | Any:  # noqa
        if "data" not in self.json or self.json['data'] in [None, [], {}]:
            return None
        if self.collection:
            return self._parse_items_as_objects(self.collection)
        return self._parse_items_as_dict()

    def items_as(self, collection: T) -> List[T] | None:  # noqa
        items_data = self._parse_items_as_dict()
        return None if items_data is None else TypeAdapter(List[collection]).validate_python(items_data)

    def items_as_dict(self) -> list[dict] | None:  # noqa
        if "data" not in self.json or self.json['data'] in [None, [], {}]:
            return None
        return self._parse_items_as_dict()

    @property
    def total_count(self) -> int:
        if "meta" in self.json and "total_count" in self.json['meta']:
            return self.json['meta']['total_count']

    @property
    def filtered_count(self) -> int:
        if "meta" in self.json and "filter_count" in self.json['meta']:
            return self.json['meta']['filter_count']

    @property
    def status_code(self) -> int:
        return getattr(self.response, 'status_code', 0)

    @property
    def is_success(self) -> bool:
        return self.status_code in [200, 201, 204, 304]

    @property
    def is_error(self) -> bool:
        return not self.is_success

    @property
    def errors(self) -> list:
        if self.is_error and "errors" in self.json:
            return self.json['errors']
        else:
            return []

    def get_explanation(self, show_headers=True, show_cookies=True) -> dict:
        needed_data = {}

        ''' Request '''
        
        resp_request = self.response.request

        request_data = {
            "method": resp_request.method,
            "url": str(resp_request.url)
        }

        # headers
        if show_headers:
            request_data["headers"] = self.response.headers.multi_items()

        # extensions
        request_data["extensions"] = resp_request.extensions

        needed_data["Request"] = request_data

        ''' Response '''

        response_data = {
            "status_code": self.response.status_code
        }

        # headers
        if show_headers:
            response_data["headers"] = self.response.headers.multi_items()

        # cookies
        if show_cookies:
            cookies = self.response.cookies

            response_data["cookies"] = [
                f"<Cookie {cookie.name}={cookie.value} for {cookie.domain} />"
                for cookie in cookies.jar
            ]

        # data
        response_data.update(self.response.json())

        needed_data["Response"] = response_data

        return needed_data

    def print_explanation(self, show_headers=True, show_cookies=True):
        needed_data = self.get_explanation(show_headers=show_headers, show_cookies=show_cookies)

        print(needed_data)


class DirectusException(Exception):
    def __init__(self, response: DirectusResponse):
        self.response = response
        self.status_code = response.status_code
        self.message = None
        self.code = None

        if len(response.errors) > 0 and (
            "message" in response.errors[0] 
            and "extensions" in response.errors[0] 
            and "code" in response.errors[0]['extensions']
        ):
            self.message = response.errors[0]['message']
            self.code = response.errors[0]['extensions']['code']

    def __str__(self):
        return f"{self.code}: {self.message}"
