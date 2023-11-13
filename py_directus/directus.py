import os
import re
import datetime
import inspect
import magic
from typing import Optional, Type

from httpx import AsyncClient, Auth, Response
from pydantic import BaseModel

from py_directus.directus_request import DirectusRequest
from py_directus.directus_response import DirectusResponse
from py_directus.models import Role, User
from py_directus.transformation import ImageFileTransform
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

    def __init__(
        self, url: str, email: str = None, password: str = None, token: str = None, refresh_token: str = None,
        connection: AsyncClient = None, user_model: Type[User] = User
    ):
        self.expires = None
        self.expiration_time = None
        self.refresh_token = refresh_token
        self.url: str = url

        self._token: Optional[str] = None
        self._user: User | None = None
        self._user_model: Type[User] = user_model

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

    async def me(self, user_model: Type[User] | str | None = None) -> DirectusResponse:
        """
        Retrieve logged in user's information.
        """

        if not user_model:
            user_model = self._user_model

        response_obj = await self.collection(user_model).read("me")

        return response_obj

    async def roles(self) -> DirectusResponse:
        """
        Retrieve list of roles in system.
        """

        response_obj = await self.collection(Role).read()
        return response_obj

    async def read_settings(self) -> DirectusResponse:
        response_obj = await DirectusRequest(self, "directus_settings").read(method='get')
        return response_obj

    async def update_settings(self, data) -> DirectusResponse:
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
        """
        NOTE: TO BE REDESIGNED
        """
        response_obj = await self.collection("translations").create([{"key": key} for key in keys])
        return response_obj

    async def download_file(self, file_id: str, **kwargs) -> Response:
        url = f"{self.url}/assets/{file_id}"

        request_params = {
            "download": ""
        }

        # Image transformation parameters
        img_transform_parameters = ImageFileTransform(**kwargs).parameters

        if img_transform_parameters:
            request_params.update(img_transform_parameters)

        response = await self.connection.get(url, params=request_params)

        if response.status_code == 200:
            # Get file name
            d = response.headers['content-disposition']
            fname = re.findall("filename=[\"\'](.+)[\"\']", d)
            cln_fname = fname[0] if fname else file_id

            # Create file from received data
            with open(cln_fname, 'wb') as f:
                f.write(response.content)

        return response

    async def upload_file(self, file_path: str) -> Response:
        url = f"{self.url}/files"

        # file name with extension
        file_name = os.path.basename(file_path)
        file_mime = magic.from_file(file_path, mime=True)

        data = {
            "title": os.path.splitext(file_name)[0],
            # "folder": "foreign_key"
        }

        files = {
            "file": (file_name, open(file_path, 'rb'), file_mime)
        }

        response = await self.connection.post(url, data=data, files=files, auth=self.auth)

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
            user = await self.me()
            self._user = user.item
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

    async def logout(self) -> bool:
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
