import os
import unittest

from dotenv import load_dotenv

from py_directus import F, Directus


load_dotenv()
url = os.environ['DIRECTUS_URL']
email = os.environ['DIRECTUS_EMAIL']
password = os.environ['DIRECTUS_PASSWORD']
token = os.environ['DIRECTUS_TOKEN']


class TestFiltering(unittest.IsolatedAsyncioTestCase):
    """
    Test to see that we have a response for the written filter.
    """

    async def asyncSetUp(self):
        self.directus = await Directus(url, email=email, password=password)
    
    async def asyncTearDown(self):
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
