import os
import unittest

from dotenv import load_dotenv

try:
    from rich import print  # noqa
except:
    pass

from py_directus import F, Directus

load_dotenv()


class TestRequest(unittest.IsolatedAsyncioTestCase):
    """
    Test directus request methods.
    """

    @classmethod
    def setUpClass(cls):
        """
        Define constants on class before before running tests in the class.
        """

        cls.url = os.environ['DIRECTUS_URL']
        cls.email = os.environ['DIRECTUS_EMAIL']
        cls.password = os.environ['DIRECTUS_PASSWORD']
        cls.token = os.environ['DIRECTUS_TOKEN']

    async def asyncSetUp(self):
        """
        Initialize client before each test start.
        """

        self.directus = await Directus(self.url, email=self.email, password=self.password)

    async def asyncTearDown(self):
        """
        Close client after each test end.
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

    # NOTE: DEPRECATED, USE AGGREGATION INSTEAD
    async def test_include_count(self):
        # include_count
        jn_doe_res = await self.directus.collection("directus_users").include_count().read()

        result_items = jn_doe_res.items
        self.assertIsNotNone(result_items)

        print(f"test_include_count (total_count): {jn_doe_res.total_count}")
        print(f"test_include_count (filtered_count): {jn_doe_res.filtered_count}")

    async def test_aggregate(self):
        # aggregate
        jn_doe_res = await self.directus.collection("directus_users").aggregate().read()

        result_items = jn_doe_res.items
        self.assertIsNotNone(result_items)

        print(f"test_aggregate: {result_items}")

    async def test_group_by(self):
        # group_by
        jn_doe_res = await self.directus.collection("directus_users").group_by("first_name", "last_name").read()

        result_items = jn_doe_res.items
        self.assertIsNotNone(result_items)

        print(f"test_group_by: {result_items}")

    async def test_gather_response(self):
        # await for response
        res_1 = await self.directus.collection("directus_users").group_by("first_name", "last_name").read()
        res_2 = await self.directus.collection("directus_users").limit(10).read()
        res_1 = res_1.items
        res_2 = res_2.items

        # gather responses and await for them
        batch_1 = await self.directus.collection("directus_users").group_by("first_name", "last_name").read(
            as_task=True)
        batch_2 = await self.directus.collection("directus_users").limit(10).read(as_task=True)
        await self.directus.gather()
        batch_1 = batch_1.items
        batch_2 = batch_2.items

        self.assertIsNotNone(res_1)
        self.assertIsNotNone(res_2)
        self.assertIsNotNone(batch_1)
        self.assertIsNotNone(batch_2)
        # check if responses are equal
        self.assertEqual(res_1, batch_1)
        self.assertEqual(res_2, batch_2)
