import os
import unittest

from dotenv import load_dotenv
try:
    from rich import print  # noqa
except:
    pass

from py_directus import Directus


load_dotenv()


class TestClient(unittest.IsolatedAsyncioTestCase):
    """
    Test `Directus` asynchronous client initialization, login and logout functionality.
    """

    async def asyncSetUp(self):
        self.url = os.environ['DIRECTUS_URL']
        self.email = os.environ['DIRECTUS_EMAIL']
        self.password = os.environ['DIRECTUS_PASSWORD']
        self.token = os.environ['DIRECTUS_TOKEN']

    async def test_initialize(self):
        """
        Regular initialization.
        """
        directus = await Directus(self.url, email=self.email, password=self.password)

        # User
        user = await directus.user
        self.assertIsNotNone(user.id)

        # Logout
        await directus.logout()
        self.assertIsNone(directus._token)

        # Manually close connection
        await directus.close_connection()

    async def test_scoped_initialize(self):
        """
        Scoped client initialization.
        Here logout and connection closure are performed automatically.
        """
        async with await Directus(self.url, email=self.email, password=self.password) as directus:
            # User
            user = await directus.user
            print(user)
            self.assertIsNotNone(user.id)

    async def test_late_login(self):
        """
        Late login when client is not awaited.
        """
        directus = Directus(self.url, email=self.email, password=self.password)

        # Login
        await directus.login()
        self.assertIsNotNone(directus.token)

        # Logout
        await directus.logout()
        self.assertIsNone(directus.token)

        # Manually close connection
        await directus.close_connection()

    async def test_token_refresh(self):
        """
        Check client authentication token refresh.
        """
        async with await Directus(self.url, email=self.email, password=self.password) as directus:
            # Initial token
            old_token = directus.token
            self.assertIsNotNone(old_token)

            # Refresh
            await directus.refresh()

            new_token = directus.token
            self.assertIsNotNone(new_token)

            self.assertNotEqual(old_token, new_token)
