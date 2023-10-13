import unittest
import json

from py_directus import F


class TestFilterObject(unittest.TestCase):
    """
    Test to see what we get as a result from the `F` object.
    """

    def test_filter_object(self):
        # age equals 23 and (name equals John or name equals Jane)
        my_filter = F(age=23) & (F(name="John") | F(name="Jane"))

        print(json.dumps(my_filter.query, indent=2))
