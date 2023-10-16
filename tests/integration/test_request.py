import os
import unittest

from dotenv import load_dotenv
try:
    from rich import print  # noqa
except:
    pass

from py_directus import F, Directus
from py_directus.operators import AggregationOperators


load_dotenv()


class TestRequest(unittest.IsolatedAsyncioTestCase):
    """
    Test directus request methods.
    """

    async def asyncSetUp(self):
        """
        Initialize client before tests start.
        """
        url = os.environ['DIRECTUS_URL']
        email = os.environ['DIRECTUS_EMAIL']
        password = os.environ['DIRECTUS_PASSWORD']
        token = os.environ['DIRECTUS_TOKEN']

        self.directus = await Directus(url, email=email, password=password)

    async def asyncTearDown(self):
        """
        Close client after tests end.
        """
        # Logout
        await self.directus.logout()
        await self.directus.close_connection()

    async def test_kwargs_filter(self):
        # Filter using kwargs
        jn_doe_res = await self.directus.collection("directus_users").filter(first_name="John", last_name="Doe").read()
        self.assertIsNotNone(jn_doe_res.items)

    async def test_object_filter(self):
        # Filter using the `F` object
        fltr = F(first_name="John") & F(last_name="Doe")
        jn_doe_res = await self.directus.collection("directus_users").filter(fltr).read()
        self.assertIsNotNone(jn_doe_res.items)

    async def test_sort(self):
        # sort
        jn_doe_res = await self.directus.collection("directus_users").sort(
            "first_name", asc=True
        ).sort(
            "last_name", asc=False
        ).read()

        result_items = jn_doe_res.items
        self.assertIsNotNone(result_items)

        print(f"test_sort: {result_items}")

    async def test_search(self):
        # search
        jn_doe_res = await self.directus.collection("directus_users").search("John").read()

        result_items = jn_doe_res.items
        self.assertIsNotNone(result_items)

        print(f"test_search: {result_items}")

    async def test_page(self):
        # page
        jn_doe_res = await self.directus.collection("directus_users").page().read()

        result_items = jn_doe_res.items
        self.assertIsNotNone(result_items)

        print(f"test_page: {result_items}")

    async def test_limit(self):
        # limit
        jn_doe_res = await self.directus.collection("directus_users").limit(10).read()

        result_items = jn_doe_res.items
        self.assertIsNotNone(result_items)

        print(f"test_limit: {result_items}")

    async def test_offset(self):
        # offset
        jn_doe_res = await self.directus.collection("directus_users").offset().read()

        result_items = jn_doe_res.items
        self.assertIsNotNone(result_items)

        print(f"test_offset: {result_items}")

    async def test_include_count(self):
        # include_count
        jn_doe_res = await self.directus.collection("directus_users").include_count().read()

        result_items = jn_doe_res.items
        self.assertIsNotNone(result_items)

        print(f"test_include_count: {result_items}")

    async def test_aggregate(self):
        # include_count
        jn_doe_res = await self.directus.collection("directus_users").aggregate(AggregationOperators.Count).read()

        result_items = jn_doe_res.items
        self.assertIsNotNone(result_items)

        print(f"test_aggregate: {result_items}")

    async def test_group_by(self):
        # include_count
        jn_doe_res = await self.directus.collection("directus_users").group_by("first_name", "last_name").read()

        result_items = jn_doe_res.items
        self.assertIsNotNone(result_items)

        print(f"test_group_by: {result_items}")
