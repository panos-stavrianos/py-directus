import os
import unittest
from dotenv import load_dotenv

import py_directus
from tests.integration.example_models import DirectusModels

try:
    from rich import print  # noqa
except:
    pass

load_dotenv()


class TestExtendModels(unittest.IsolatedAsyncioTestCase):
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

    async def test_extend_models(self):
        await py_directus.async_init(self.url, self.token, directus_models=DirectusModels)
        assert 'pet' in py_directus.DirectusUser.model_fields
        assert 'overlord' in py_directus.DirectusRole.model_fields

    async def test_nested_models(self):
        await py_directus.async_init(self.url, self.token, directus_models=DirectusModels)
        print(py_directus.DirectusUser.model_fields)
        # assert py_directus.DirectusUser.model_fields['role'].annotation == Role
