from __future__ import annotations

import asyncio
import json as jsonlib
from typing import (
    TYPE_CHECKING,
    Union, Optional, Type, List, Tuple,
    overload
)

import json_fix
import websockets
from pydantic import BaseModel

from py_directus.aggregator import Agg
from py_directus.directus_response import DirectusResponse
from py_directus.filter import F

# from py_directus.operators import AggregationOperators

if TYPE_CHECKING:
    from websockets import Data, WebSocketClientProtocol
    from py_directus import Directus


class DirectusRequest:
    """
    Class to manage request to the Directus API.
    """
    _lock = asyncio.Lock()
    _lock_2 = asyncio.Lock()

    def __init__(self, directus: 'Directus', collection: str,
                 collection_class: Optional[Union[Type[BaseModel], str]] = None):
        json_fix.fix_it()

        self.directus: 'Directus' = directus
        self.collection: str = collection
        self.params: dict = {}
        self.collection_class: Optional[Union[Type[BaseModel], str]] = collection_class

    @property
    def uri(self):
        if "directus_" in self.collection:
            return f"{self.directus.url}/{self.collection.replace('directus_', '')}"
        return f"{self.directus.url}/items/{self.collection}"

    def fields(self, *fields):
        self.params['fields'] = ",".join(fields)
        return self

    def filter(self, *args, **filters):
        """
        :param operator: The operator to use for the filter (Operators.Equals)
        :param logical_operator: The logical operator to use for the filter (LogicalOperators.And)
        :param filters: Multiple filters to use

        :return: The DirectusRequest object

        :example:
                .filter(Operators.Equals, LogicalOperators.Or, first_name="Panos", location=None) \
                .filter(Operators.Equals, last_name="Stavrianos") \
        """
        # Argument handling
        clean_args = list(filter(lambda x: isinstance(x, F), args))

        new_args_filter = None
        if clean_args:
            new_args_filter = clean_args[0]

            for fltr in clean_args[1:]:
                new_args_filter &= fltr

            if "filter" in self.params:
                self.params['filter'] = self.params['filter'] & new_args_filter
            else:
                self.params['filter'] = new_args_filter

        # Keyword argument handling
        # filter_param = Filter(operator, logical_operator, **filters)
        filter_param = F(**filters)

        if "filter" in self.params:
            self.params['filter'] = self.params['filter'] & filter_param
        else:
            self.params['filter'] = filter_param

        return self

    def sort(self, field, asc=True):
        if 'sort' not in self.params:
            self.params['sort'] = []
        self.params['sort'].append(f'{"" if asc else "-"}{field}')
        return self

    def search(self, search: Optional[Union[str, int]] = None):
        self.params['search'] = search
        return self

    def page(self, page: int = 1):
        self.params['page'] = page
        return self

    def limit(self, limit: int = -1):
        self.params['limit'] = limit
        return self

    def offset(self, offset: int = 0):
        self.params['offset'] = offset
        return self

    def aggregate(self, *args, **aggregates):
        """
        :param operator: The operator to use for the aggregation (AggregationOperators.Count)
        :param field: Field name uppon which the aggregation will be performed

        :return: The DirectusRequest object
        """

        # Argument handling
        clean_args = list(filter(lambda x: isinstance(x, Agg), args))

        new_args_aggregator = None
        if clean_args:
            new_args_aggregator = clean_args[0]

            for aggr in clean_args[1:]:
                new_args_aggregator += aggr

            if "aggregate" in self.params:
                self.params['aggregate'] = self.params['aggregate'] + new_args_aggregator
            else:
                self.params['aggregate'] = new_args_aggregator

        # Keyword argument handling
        aggregator_param = Agg(**aggregates)

        if "aggregate" in self.params:
            self.params['aggregate'] = self.params['aggregate'] + aggregator_param
        else:
            self.params['aggregate'] = aggregator_param

        return self

    def group_by(self, *fields):
        self.params['groupBy'] = ",".join(fields)
        return self

    def include_count(self):
        # NOTE: DEPRECATED, USE AGGREGATION INSTEAD
        self.params['meta'] = "*"
        return self

    async def read(
            self, id: Optional[Union[int, str]] = None, method: str = "search", cache: bool = False,
            as_task: bool = False
    ) -> DirectusResponse:
        """
        Request data.

        :param id: The id of the item to retrieve
        :param method: The method to use for the request (search, get)
        :param cache: Whether to use the cache or not
        :param as_task: Whether to add the request to the tasks list or not (for batch requests)

        :return: The DirectusResponse object

        IMPORTANT: cache and as_task cannot be used together, if both are set to True, the cache will take precedence and the request will be awaited.
        """
        cache = False  # TODO: Temporary disable until cache is fixed
        if cache:
            d_response = await self._read_cache(id=id, method=method)
        else:
            d_response = await self._read(id=id, method=method, as_task=as_task)

        return d_response

    async def _read(
            self, id: Optional[Union[int, str]] = None, method: str = "search", renew_cache: bool = False,
            as_task: bool = False
    ) -> DirectusResponse:
        """
        Send query to server.
        """

        method = "get" if id is not None else method
        if method == "search":
            response = self.directus.connection.request(
                "search", self.uri,
                json={"query": self.params},
                auth=self.directus.auth
            )
        elif method == "get":
            url = f"{self.uri}/{id}" if id is not None else self.uri
            response = self.directus.connection.get(url, params=self.params, auth=self.directus.auth)
        else:
            raise ValueError(f"Method '{method}' not supported")

        d_response = DirectusResponse(response, query=self.params, collection=self.collection_class)

        if as_task:
            self.directus.tasks.append(d_response)
        else:
            await d_response.gather_response()

        # Check for existing cache and renew it
        if not renew_cache:
            async with self._lock_2:
                query_key_str = self._get_query_string_key()

                # Try to find query in cache
                cached_response = await self.directus.cache.get(query_key_str)

                if cached_response:
                    # Renew the cache value
                    await self.directus.cache.add(query_key_str, d_response.to_json())

        return d_response

    async def _read_cache(
            self, id: Optional[Union[int, str]] = None, method: str = "search"
    ) -> DirectusResponse:
        """
        Get response from cache.
        """
        async with self._lock:
            query_key_str = self._get_query_string_key()

            # Try to find query in cache
            cached_response = await self.directus.cache.get(query_key_str)

            if cached_response:
                print("FROM CACHE")
                d_response = DirectusResponse.from_json(cached_response, collection=self.collection_class)
            else:
                print("FROM NEW")
                d_response = await self._read(id=id, method=method, renew_cache=True)

                # Add results to cache
                await self.directus.cache.add(query_key_str, d_response.to_json())

            return d_response

    async def clear_cache(self):
        query_key_str = self._get_query_string_key()

        # Try to find query in cache
        d_res = await self.directus.cache.delete(query_key_str)
        return d_res

    def _get_query_string_key(self):
        """
        Generate request key for cache.
        """

        query_str = jsonlib.dumps(self.params)

        return f"{self.collection}_{query_str}"

    async def subscribe(self, uri: str, event_type: Optional[str] = None, uid: Optional[str] = None) -> Tuple[
        'Data', 'WebSocketClientProtocol']:
        """
        Returns authentication confirmation message and the client websocket.
        """
        ws = await websockets.connect(uri)

        # Authentication
        auth_data = jsonlib.dumps({
            "type": "auth",
            "access_token": self.directus._token
        })

        await ws.send(auth_data)
        auth_res = await ws.recv()

        # Subscription
        subsc_data = {
            "type": "subscribe",
            "collection": self.collection,
            "query": self.params
        }

        if event_type:
            subsc_data['event'] = event_type

        if uid:
            subsc_data['uid'] = uid

        await ws.send(jsonlib.dumps(subsc_data))
        subsc_res = await ws.recv()

        return auth_res, ws

    async def create(self, items: Union[dict, List[dict]], as_task: bool = False) -> DirectusResponse:
        assert isinstance(items, (dict, list))

        response = self.directus.connection.post(self.uri, json=items, auth=self.directus.auth)
        d_response = DirectusResponse(response, collection=self.collection_class)
        if as_task:
            self.directus.tasks.append(d_response)
        else:
            await d_response.gather_response()
        return d_response

    @overload
    async def update(self, ids: Optional[Union[int, str]], items: dict, as_task: bool = False) -> DirectusResponse:
        ...

    @overload
    async def update(self, ids: List[Union[int, str]], items: list, as_task: bool = False) -> DirectusResponse:
        ...

    async def update(self, ids, items, as_task: bool = False) -> DirectusResponse:
        if isinstance(ids, (int, str, None)) and isinstance(items, dict):
            if ids is None:
                response = self.directus.connection.patch(self.uri, json=items, auth=self.directus.auth)
            else:
                response = self.directus.connection.patch(f"{self.uri}/{ids}", json=items, auth=self.directus.auth)
            d_response = DirectusResponse(response, collection=self.collection_class)
        elif isinstance(ids, list) and isinstance(items, list):
            payload = {
                "keys": ids,
                "data": items
            }
            response = self.directus.connection.patch(self.uri, json=payload, auth=self.directus.auth)
            d_response = DirectusResponse(response, collection=self.collection_class)
        else:
            raise TypeError(
                f"This method supports the following argument pairs: \n"
                f"ids: int | str | None, items: dict\n"
                f"ids: list[int | str], items: list\n"
                f"You provided: ids={type(ids)}, items={type(items)}"
            )
        if as_task:
            self.directus.tasks.append(d_response)
        else:
            await d_response.gather_response()
        return d_response

    async def delete(self, ids: Union[int, str, List[Union[int, str]]], as_task: bool = False) -> DirectusResponse:
        if isinstance(ids, (int, str)):
            response = self.directus.connection.delete(f'{self.uri}/{ids}', auth=self.directus.auth)
            d_response = DirectusResponse(response, collection=self.collection_class)
        elif isinstance(ids, list):
            response = self.directus.connection.delete(self.uri, json=ids, auth=self.directus.auth)
            d_response = DirectusResponse(response, collection=self.collection_class)
        else:
            raise TypeError(
                f"The ids argument must be one of the following types: int | str | list[int | str]\n"
                f"You provided: {ids}"
            )
        if as_task:
            self.directus.tasks.append(d_response)
        else:
            await d_response.gather_response()
        return d_response
