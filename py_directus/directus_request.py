from __future__ import annotations

from typing import Optional

import json_fix

from py_directus.directus_response import DirectusResponse
from py_directus.operators import AggregationOperators
from py_directus.filter import F


class DirectusRequest:
    """
    Class to manage request to the Directus API.
    """

    def __init__(self, directus: "Directus", collection: str, collection_class=None):
        json_fix.fix_it()
        self.directus: "Directus" = directus
        self.collection: str = collection
        self.params: dict = {}
        self.collection_class = collection_class

    @property
    def uri(self):
        if "directus_" in self.collection:
            return f"{self.directus.url}/{self.collection.replace('directus_', '')}"
        return f'{self.directus.url}/items/{self.collection}'

    def fields(self, *fields):
        self.params['fields'] = ','.join(fields)
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

    def search(self, search: str | int = None):
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

    def include_count(self):
        self.params['meta'] = '*'
        return self

    def aggregate(self, operator: AggregationOperators = AggregationOperators.Count, field='*'):
        """
        :param operator: The operator to use for the aggregation (AggregationOperators.Count)
        :param field: Field name uppon which the aggregation will be performed

        :return: The DirectusRequest object
        """
        self.params['aggregate'] = {operator.value: field}
        return self

    def group_by(self, *fields):
        self.params['groupBy'] = ','.join(fields)
        return self

    # def read_one(self, id: int | str) -> DirectusResponse:
    #     response = self.directus.session.get(f'{self.uri}/{id}', params=self.params, auth=self.directus.auth)
    #     return DirectusResponse(response)
    #
    # def read_many(self, method="search") -> DirectusResponse:
    #     if method == "search":
    #         response = self.directus.session.request("search", self.uri, json={"query": self.params},
    #                                                  auth=self.directus.auth)
    #     elif method == "get":
    #         response = self.directus.session.get(self.uri, params=self.params, auth=self.directus.auth)
    #     else:
    #         raise ValueError(f"Method '{method}' not supported")
    #     return DirectusResponse(response, self.params)

    def read(self, id: Optional[int | str] = None, method="search") -> DirectusResponse:
        method = "get" if id is not None else method
        if method == "search":
            response = self.directus.connection.request(
                "search", self.uri, 
                json={"query": self.params},
                auth=self.directus.auth
            )
        elif method == "get":
            url = f'{self.uri}/{id}' if id is not None else self.uri
            response = self.directus.connection.get(url, params=self.params, auth=self.directus.auth)
        else:
            raise ValueError(f"Method '{method}' not supported")
        return DirectusResponse(response, query=self.params, collection=self.collection_class)

    def create_one(self, item: dict) -> DirectusResponse:
        response = self.directus.connection.post(self.uri, json=item, auth=self.directus.auth)
        return DirectusResponse(response, collection=self.collection_class)

    def create_many(self, items: list[dict]) -> DirectusResponse:
        response = self.directus.connection.post(self.uri, json=items, auth=self.directus.auth)
        return DirectusResponse(response, collection=self.collection_class)

    def update_one(self, id: int | str | None, item: dict) -> DirectusResponse:
        if id is None:
            response = self.directus.connection.patch(self.uri, json=item, auth=self.directus.auth)
        else:
            response = self.directus.connection.patch(f'{self.uri}/{id}', json=item, auth=self.directus.auth)
        return DirectusResponse(response, collection=self.collection_class)

    def update_many(self, ids: list[int | str], items) -> DirectusResponse:
        payload = {
            "keys": ids,
            "data": items
        }
        response = self.directus.connection.patch(self.uri, json=payload, auth=self.directus.auth)
        return DirectusResponse(response, collection=self.collection_class)

    def delete_one(self, id: int | str) -> DirectusResponse:
        response = self.directus.connection.delete(f'{self.uri}/{id}', auth=self.directus.auth)
        return DirectusResponse(response, collection=self.collection_class)

    def delete_many(self, ids: list[int | str]) -> DirectusResponse:
        response = self.directus.connection.delete(self.uri, json=ids, auth=self.directus.auth)
        return DirectusResponse(response, collection=self.collection_class)
