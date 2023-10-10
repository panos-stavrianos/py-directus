from __future__ import annotations

import inspect
import datetime
from typing import Optional, Type

from httpx import Client, Auth
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
    Client for Directus API communication.
    """

    def __init__(self, url, email=None, password=None, token=None, refresh_token=None,
                 connection: Client = None):
        self.expires = None
        self.expiration_time = None
        self.refresh_token = refresh_token
        self.url: str = url

        self._token: Optional[str] = None
        self._user: User | None = None

        self.email = email
        self.password = password
        self.static_token = token
        self.connection = connection or Client()
        self.auth = BearerAuth(self._token)
        self.token = self.static_token or None

        if self.email and self.password:
            self.login()

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

    def read_me(self):
        return DirectusRequest(self, "directus_users").read("me")

    def read_settings(self):
        return DirectusRequest(self, "directus_settings").read(method='get')

    def update_settings(self, data):
        return DirectusRequest(self, "directus_settings").update_one(None, data)

    def read_translations(self) -> dict[str, dict[str, str]]:
        items = self.items("translations").fields(
            'key', 'translations.languages_code', 'translations.translation'
        ).read().items
        return parse_translations(items)

    def download_file(self, file_id):
        return self.connection.get(f'{self.url}/assets/{file_id}')

    def create_translations(self, keys: list[str]):
        return self.items("translations").create_many([{"key": key} for key in keys])

    def __enter__(self):
        return self

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, token):
        self._token = token
        self.auth = BearerAuth(self._token)

    @property
    def user(self):
        if self._user is None:
            self._user = User(**self.read_me().item)
        return self._user

    def login(self):

        if self.static_token:
            self._token = self.static_token
            return

        url = f'{self.url}/auth/login'
        payload = {
            'email': self.email,
            'password': self.password
        }

        r = self.connection.post(url, json=payload)
        response = DirectusResponse(r)
        self._token = response.item['access_token']
        self.refresh_token = response.item['refresh_token']
        self.expires = response.item['expires']  # in milliseconds
        self.expiration_time: datetime.datetime = (
            datetime.datetime.now() + datetime.timedelta(milliseconds=self.expires)
        )
        self.auth = BearerAuth(self._token)

    def refresh(self):
        url = f'{self.url}/auth/refresh'
        payload = {
            'refresh_token': self.refresh_token,
            "mode": "json"
        }
        r = self.connection.post(url, json=payload)
        response = DirectusResponse(r)
        self.token = response.item['access_token']
        self.refresh_token = response.item['refresh_token']
        self.expires = response.item['expires']

    def logout(self):
        url = f'{self.url}/auth/logout'
        response = self.connection.post(url)
        self.connection.auth = None
        return response.status_code == 200

    def close_connection(self):
        self.connection.close()

    def __exit__(self, *args):
        # Exception handling here
        self.logout()
        self.close_connection()
