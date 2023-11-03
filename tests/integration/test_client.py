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

    @classmethod
    def setUpClass(cls):
        """
        Define constants on class before before running tests in the class.
        """

        cls.url = os.environ['DIRECTUS_URL']
        cls.email = os.environ['DIRECTUS_EMAIL']
        cls.password = os.environ['DIRECTUS_PASSWORD']
        cls.token = os.environ['DIRECTUS_TOKEN']

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

            # directus.collection("directus_users").aggregate()  # count("*")
            # directus.collection("directus_users").aggregate("*")  # count("*")
            # directus.collection("directus_users").aggregate(count="name")  # count("name")
            # directus.collection("directus_users").aggregate("*", sum="name", )  # count("*"), sum("name")

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

    async def test_me(self):
        """
        Check client 'me' method.
        """
        async with await Directus(self.url, email=self.email, password=self.password) as directus:
            # Me
            me_resp = await directus.me()
            me_obj = me_resp.item

            print(me_obj)

    async def test_roles(self):
        """
        Check client 'roles' method.
        """
        async with await Directus(self.url, email=self.email, password=self.password) as directus:
            # Roles
            roles_resp = await directus.roles()
            roles = roles_resp.items

            print(roles)
