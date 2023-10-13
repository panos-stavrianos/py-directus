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
    async def test_login(self):
        print("Testing login 3")
        directus = await Directus(url, email=email, password=password)
        user = await directus.user
        print(user)
        self.assertIsNotNone(user.id)
        await directus.logout()
        self.assertIsNone(directus._token)

    async def test_login_context_manager(self):
        print("IN ASYNC test_login_context_manager")
        async with await Directus(url, email=email, password=password) as directus:
            user = await directus.user
            print(user)
            self.assertIsNotNone(user.id)
