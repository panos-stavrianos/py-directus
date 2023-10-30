import json

from py_directus.operators import AggregationOperators


class Agg:
    """
    Aggregation field.
    """

    def __init__(self, operator: AggregationOperators = AggregationOperators.Count, fields='*'):
        # Initialize the query as an empty dictionary
        self.query = {}

        self.query = {operator.value: fields}

    def __str__(self):
        return f"\n{json.dumps(self.query, indent=2)}\n"

    def __json__(self):
        return json.dumps(self.query, indent=2)
