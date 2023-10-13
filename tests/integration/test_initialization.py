import os
import unittest

from dotenv import load_dotenv

from py_directus import Directus


load_dotenv()
url = os.environ['DIRECTUS_URL']
email = os.environ['DIRECTUS_EMAIL']
password = os.environ['DIRECTUS_PASSWORD']
token = os.environ['DIRECTUS_TOKEN']


class TestInitialization(unittest.IsolatedAsyncioTestCase):
    """
    Test `Directus` asynchronous client initialization, login and logout functionality.
    """

    async def test_login(self):
        directus = await Directus(url, email=email, password=password)

        # Login
        user = await directus.user
        self.assertIsNotNone(user.id)

        # Logout
        await directus.logout()
        self.assertIsNone(directus._token)

        # Manually close connection
        await directus.close_connection()

    async def test_login_context_manager(self):
        async with await Directus(url, email=email, password=password) as directus:
            user = await directus.user
            print(user)
            self.assertIsNotNone(user.id)
