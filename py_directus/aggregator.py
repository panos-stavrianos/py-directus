import json
from typing import List
from functools import singledispatchmethod

from py_directus.operators import AGGREGATION_OPERATORS, AggregationOperators


class Agg:
    """
    Aggregation field.
    """

    @singledispatchmethod
    def __init__(self, operator, fields):
        raise NotImplementedError("No comment")

    @__init__.register
    def _normal(self, operator: AggregationOperators | None = AggregationOperators.Count, fields: str | List[str] | None = '*'):
        # Initialize the query as an empty dictionary
        self.query = {}

        # Add given arguments
        self.add(operator, fields)

    @__init__.register
    def _from_string(self, field_def: str):
        # Initialize the query as an empty dictionary
        self.query = {}

        # Clean arguments
        field, operator = Agg.parse_key(field_def)

        # Add given arguments
        self.add(operator, field)
    
    @staticmethod
    def parse_key(key):
        field = None
        operator = None

        for _operator in AGGREGATION_OPERATORS:
            if key.endswith("_" + _operator):
                field = key[:-len("_" + _operator)]
                operator = _operator
                break

        field = field.replace("__", ".")
        operator = operator[1:]

        if field == "":
            field = None
        return field, operator

    def add(self, operator: AggregationOperators | str | None = None, fields: str | List[str] | None = None):
        if operator and fields:
            if isinstance(operator, AggregationOperators):
                needed_operator = operator.value
            else:
                needed_operator = operator

            if needed_operator in self.query:
                orig_value = self.query[needed_operator]

                # Encapsulate the value in a list
                if not isinstance(orig_value, list):
                    orig_value = [orig_value]

                # Add fields to value list
                if isinstance(fields, list):
                    orig_value = [*orig_value, *fields]
                else:
                    orig_value.append(fields)

                self.query[needed_operator] = orig_value
            else:
                self.query[needed_operator] = fields

    def __and__(self, other: 'Agg'):
        # Implement the logical AND operator
        for operator, fields in other.query.items():
            self.add(operator, fields)
        return self

    def __str__(self):
        return f"\n{json.dumps(self.query, indent=2)}\n"

    def __json__(self):
        return json.dumps(self.query, indent=2)
