import json
from typing import Union, List

from py_directus.expression import Expression
from py_directus.operators import AGGREGATION_OPERATORS, AggregationOperators


class Agg(Expression):
    """
    Aggregation field.
    """

    def __init__(self, *args, **kwargs):
        # Initialize the query as an empty dictionary
        self.query = {}

        # Arguments
        for arg in args:
            if isinstance(arg, str):
                self._from_string(arg)
        
        # Operator
        if "operator" in kwargs or "fields" in kwargs:
            kwrg_operator = kwargs.pop("operator", None)
            kwrg_fields = kwargs.pop("fields", None)

            self._from_operator(kwrg_operator, kwrg_fields)

        # Keyword Arguments
        for key, value in kwargs.items():
            self._from_kwarg(key, value)

        if not self.query:
            self.query["count"] = "*"

    def _from_operator(self, operator: Union[AggregationOperators, None] = AggregationOperators.Count, fields: Union[str, List[str], None] = "*"):
        # Clean arguments
        if isinstance(fields, list):
            cln_fields = [Agg.parse_key(fld)[0] for fld in fields]
        else:
            cln_fields = Agg.parse_key(fields)[0]

        # Add given arguments
        self._add(operator, cln_fields)

    def _from_string(self, field_def: str):
        # Clean arguments
        field, operator = Agg.parse_key(field_def)

        # Add given arguments
        self._add(operator, field)
    
    def _from_kwarg(self, operator: str, fields: Union[str, List[str]]):
        # Clean arguments
        if isinstance(fields, list):
            cln_fields = [Agg.parse_key(fld)[0] for fld in fields]
        else:
            cln_fields = Agg.parse_key(fields)[0]

        # Add given arguments
        self._add(operator, cln_fields)

    @staticmethod
    def parse_key(key):
        field = None
        operator = None

        for _operator in AGGREGATION_OPERATORS:
            if key.endswith("_" + _operator):
                field = key[:-len("_" + _operator)]
                operator = _operator
                break

        # No operator matched, which we assume was not provided.
        # Thus we use the default 'count' operator.
        if field is None:
            operator = "count"
            field = key.replace("__", ".")
            return field, operator

        # Deep fields
        field = field.replace("__", ".")

        if operator:
            operator = operator[1:]

        if field == "":
            field = None
        return field, operator

    def _add(self, operator: Union[AggregationOperators, str, None] = None, fields: Union[str, List[str], None] = None):
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

    def __add__(self, other: 'Agg'):
        # Implement addition logic
        for operator, fields in other.query.items():
            self._add(operator, fields)
        return self

    def __str__(self):
        return f"\n{json.dumps(self.query, indent=2)}\n"

    def __json__(self):
        return json.dumps(self.query, indent=2)
