import datetime
import inspect
from typing import Optional, Type

from httpx import AsyncClient, Auth
from pydantic import BaseModel

from py_directus.directus_request import DirectusRequest
from py_directus.directus_response import DirectusResponse
from py_directus.models import User
from py_directus.utils import parse_translations


class BearerAuth(Auth):
    def __init__(self, token: str):
        self.token = token

    def auth_flow(self, request):
        if self.token is not None:
            request.headers["Authorization"] = f"Bearer {self.token}"
        yield request


class Directus:
    """
    Asynchronous Client for Directus API communication.
    """

    def __init__(self, url, email=None, password=None, token=None, refresh_token=None,
                 connection: AsyncClient = None):
        self.expires = None
        self.expiration_time = None
        self.refresh_token = refresh_token
        self.url: str = url

        self._token: Optional[str] = None
        self._user: User | None = None

        self.email = email
        self.password = password
        self.static_token = token
        self.connection = connection or AsyncClient()
        self.auth = BearerAuth(self._token)
        self.token = self.static_token or None

    def __await__(self):
        async def closure():
            # Perform login when credentials are present and no token
            if self.email and self.password and not self._token:
                await self.login()
            return self

        return closure().__await__()

    # @classmethod
    # async def create(cls, url, email=None, password=None, token=None, refresh_token=None, 
    #                  connection: AsyncClient = None):
    #     client = cls(url, email, password, token, refresh_token, connection)

    #     if client.email and client.password:
    #         await client.login()
    #     return client

    def collection(self, collection: Type[BaseModel] | str) -> DirectusRequest:
        """
        Set collection to be used.
        """

        if inspect.isclass(collection):
            assert issubclass(collection, BaseModel), (
                f"The provided collection model must be a subclass of pydantic.BaseModel"
            )
            assert collection.Config.collection is not None
            return DirectusRequest(self, collection.Config.collection, collection)
        elif isinstance(collection, str):
            return DirectusRequest(self, collection, None)

        raise TypeError(
            f"The `collection` argument must be either a string or a subclass of the pydantic.BaseModel class.\n"
            f"You gave: {collection}"
        )

    async def read_me(self):
        response_obj = await DirectusRequest(self, "directus_users").read("me")
        return response_obj

    async def read_settings(self):
        response_obj = await DirectusRequest(self, "directus_settings").read(method='get')
        return response_obj

    async def update_settings(self, data):
        response_obj = await DirectusRequest(self, "directus_settings").update(None, data)
        return response_obj

    async def read_translations(self) -> dict[str, dict[str, str]]:
        """
        NOTE: TO BE REDESIGNED
        """

        items = await self.collection("translations").fields(
            'key', 'translations.languages_code', 'translations.translation'
        ).read().items

        return parse_translations(items)

    async def create_translations(self, keys: list[str]):
        response_obj = await self.collection("translations").create([{"key": key} for key in keys])
        return response_obj

    async def download_file(self, file_id):
        response = await self.connection.get(f'{self.url}/assets/{file_id}')
        return response

    async def __aenter__(self):
        return self

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, token):
        self._token = token
        self.auth = BearerAuth(self._token)

    @property
    async def user(self):
        if self._user is None:
            user = await self.read_me()
            self._user = User(**user.item)
        return self._user

    async def auth_request(self, endpoint, payload):
        url = f"{self.url}/{endpoint}"

        r = await self.connection.post(url, json=payload)
        response = DirectusResponse(r)

        self._token = response.item['access_token']
        self.refresh_token = response.item['refresh_token']
        self.expires = response.item['expires']  # in milliseconds
        self.expiration_time: datetime.datetime = (
            datetime.datetime.now() + datetime.timedelta(milliseconds=self.expires)
        )
        self.auth = BearerAuth(self._token)

    async def login(self):
        endpoint = "auth/login"

        if self.static_token:
            self._token = self.static_token
            return

        payload = {
            'email': self.email,
            'password': self.password
        }
        await self.auth_request(endpoint, payload)

    async def refresh(self):
        endpoint = "auth/refresh"
        payload = {
            'refresh_token': self.refresh_token,
            "mode": "json"
        }
        await self.auth_request(endpoint, payload)

    async def logout(self):
        url = f"{self.url}/auth/logout"
        response = await self.connection.post(url)

        self.connection.auth = None
        self._token = None
        self.refresh_token = None
        self.expires = None
        self.expiration_time = None

        return response.status_code == 200

    async def close_connection(self):
        await self.connection.aclose()

    async def __aexit__(self, *args):
        print("Closing connection")
        # Exception handling here
        await self.logout()
        await self.close_connection()
