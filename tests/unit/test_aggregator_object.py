import unittest

try:
    from rich import print  # noqa
except:
    pass

from py_directus.aggregator import Agg
from py_directus.operators import AggregationOperators


class TestAggregatorObject(unittest.TestCase):
    """
    Test to see what we get as a result from the `Agg` object.
    """

    def test_agg_object(self):
        aggregate = Agg("id__count")

        print(f"aggregate: {aggregate}")

        kwarg_aggregate = Agg(count=['accepted', 'noted'], sum="price")

        print(f"kwarg_aggregate: {kwarg_aggregate}")

        complex_aggregate = (
            Agg(operator=AggregationOperators.Count, fields=['id', 'name']) 
            + Agg(operator=AggregationOperators.Sum, fields='amount')
        )

        print(f"complex_aggregate: {complex_aggregate}")
