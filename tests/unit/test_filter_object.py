import unittest
import json

from py_directus import F


class TestFilterObject(unittest.TestCase):
    """
    Test to see what we get as a result from the `F` object.
    """

    def test_filter_object(self):
        # age equals 23
        filter_attr = F(age=23)
        print(f"Filter attribute equal: {filter_attr}")

        # age greater than 23
        filter_attr_gt = F(age__gt=23)
        print(f"Filter attribute greater: {filter_attr_gt}")

        # age greater than and equal to 23
        filter_multi_attr = F(name__contains="John", age__gt=23)
        print(f"Multiple attribute filter: {filter_multi_attr}")

        ### Deep field filter

        filter_deep_attr = F(user__name__contains="John")
        print(f"Deep attribute filter: {filter_deep_attr}")

        ### Combine filters

        # age equals 23 and name equals John
        filter_comb_and = F(age=23) & F(name="John")
        print(f"Combined filter AND: {filter_comb_and}")

        # age equals 23 or name equals John
        filter_comb_or = F(age=23) | F(name="John")
        print(f"Combined filter OR: {filter_comb_or}")

        # age equals 23 and (name equals John or name equals Jane)
        complex_filter = F(age=23) & (F(name="John") | F(name="Jane"))

        print(json.dumps(complex_filter.query, indent=2))
