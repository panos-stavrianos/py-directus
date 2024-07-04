import os
import re
import asyncio
import datetime
import inspect
from io import BytesIO
# import aiofiles
from typing import (
    TYPE_CHECKING,
    Union, Optional,
    Type, Any, List, Dict, Tuple
)

import magic
from httpx import AsyncClient, Auth, Response
from pydantic import BaseModel

import py_directus
from py_directus.cache import SimpleMemoryCache
from py_directus.directus_request import DirectusRequest
from py_directus.directus_response import DirectusResponse
from py_directus.storage import save_file
from py_directus.transformation import ImageFileTransform
from py_directus.utils import parse_translations

try:
    from starlette.datastructures import UploadFile
except ImportError:
    UploadFile = None


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
            self, url: str, email: str = None, password: str = None,
            token: str = None, refresh_token: str = None,
            connection: AsyncClient = None
    ):
        self.expires = None
        self.expiration_time = None
        self.refresh_token = refresh_token
        self.url: str = url

        # Credentials
        self._token: Optional[str] = None
        self._user: Optional['py_directus.DirectusUser'] = None

        self.email = email
        self.password = password

        self.static_token = token
        self.token = token or None

        # Connection
        self.connection = connection or AsyncClient()
        self.auth = BearerAuth(self._token)

        # Cache
        self.cache: Union[SimpleMemoryCache, None] = None

        # Any async tasks for later gathering
        self.tasks: List[DirectusResponse] = []

    def __await__(self):
        async def closure():
            # Perform login when credentials are present and no token
            if self.email and self.password and not self._token:
                await self.login()
            if not self.cache:
                await self.start_cache()
            return self

        return closure().__await__()

    async def gather(self):
        """
        Gather all async tasks.
        """
        print("Gathering tasks", self.tasks)
        await asyncio.gather(*[task.gather_response() for task in self.tasks])
        self.tasks.clear()['data']

    async def clear_cache(self):
        "Clear directus cache"
        url = f"{self.url}/utils/cache/clear"
        await self.connection.get(url, auth=self.auth)

    async def list_collections(self) -> List[Dict[str, Any]]:
        """
        Return the list of collections in the Directus instance.

        see: https://docs.directus.io/reference/system/collections.html#the-collection-object

        """
        url = f"{self.url}/collections"
        response = await self.connection.get(url, auth=self.auth)
        return response.json()['data']


    def collection(self, collection: Union[Type[BaseModel], str]) -> DirectusRequest:
        """
        Set collection to be used.
        """

        if inspect.isclass(collection):
            assert issubclass(collection, BaseModel), (
                f"The provided collection model must be a subclass of pydantic.BaseModel"
            )

            collection_name = collection.model_config.get("collection", None)

            assert collection_name is not None

            return DirectusRequest(self, collection_name, collection)
        elif isinstance(collection, str):
            return DirectusRequest(self, collection, None)

        raise TypeError(
            f"The `collection` argument must be either a string or a subclass of the pydantic.BaseModel class.\n"
            f"You gave: {collection}"
        )

    async def me(self, cache=False, as_task=False) -> DirectusResponse:
        """
        Retrieve logged in user's information.
        """
        return await self.collection(py_directus.DirectusUser).read("me", cache=cache, as_task=as_task)

    async def roles(self) -> DirectusResponse:
        """
        Retrieve list of roles in system.
        """

        response_obj = await self.collection(py_directus.DirectusRole).read()
        return response_obj

    @classmethod
    def get_file_url(
            cls, file_id: str,
            fit: Optional[str] = None,
            width: Optional[int] = None, height: Optional[int] = None,
            quality: Optional[int] = None,
            withoutEnlargement: Optional[bool] = None,
            img_format: Optional[str] = None,
            **kwargs
    ) -> str:
        """
        Generate endpoint for a specific file with transformation parameters.

        :param file_id: UUID of the file record in Directus.
        """
        url = f"{py_directus.directus_url}/assets/{file_id}"

        # Image transformation parameters
        img_transform_parameters = ImageFileTransform(
            fit=fit,
            width=width,
            height=height,
            quality=quality,
            withoutEnlargement=withoutEnlargement,
            img_format=img_format,
            **kwargs
        ).parameters

        if img_transform_parameters:
            url += "?" + "&".join([f"{k}={v}" for k, v in img_transform_parameters.items()])

        return url

    async def download_file(
            self, file_id: str,
            fit: Optional[str] = None,
            width: Optional[int] = None, height: Optional[int] = None,
            quality: Optional[int] = None,
            withoutEnlargement: Optional[bool] = None,
            img_format: Optional[str] = None,
            **kwargs
    ) -> Response:
        """
        Download a file from Directus.

        :param file_id: UUID of the file record in Directus.
        """
        url = f"{self.url}/assets/{file_id}"

        request_params = {
            "download": ""
        }

        # Image transformation parameters
        img_transform_parameters = ImageFileTransform(
            fit=fit,
            width=width,
            height=height,
            quality=quality,
            withoutEnlargement=withoutEnlargement,
            img_format=img_format,
            **kwargs
        ).parameters

        if img_transform_parameters:
            request_params.update(img_transform_parameters)

        response = await self.connection.get(url, params=request_params)

        if response.status_code == 200:
            # Get file name
            d = response.headers['content-disposition']
            fname = re.findall("filename=[\"\'](.+)[\"\']", d)
            cln_fname = fname[0] if fname else file_id

            await save_file(cln_fname, response.content)

        return response

    async def upload_file(self, to_upload: Union[str, 'UploadFile'],
                          folder: str = "", title: str ="",
                          filename_download: str ="") -> DirectusResponse:
        """
        Upload a file to Directus.

        :param to_upload: full path to file as a string or a `starlette.UploadFile` object.
        :param folder: (optional) name of a `directus_folder` collection record.
        :param title: (optional) specify the file Title. If not provided, the file name will be used.
        :param filename_download: (optional) specify the file name for download. If not provided, the file name will be used.
        """
        url = f"{self.url}/files"

        folder_id = None
        if folder:
            folder_obj = (
                await self.collection(py_directus.DirectusFolder).fields("id").filter(name=folder).read()
            ).item

            folder_id = folder_obj.id

            assert folder_id, f"Folder '{folder}' not found"

        if isinstance(to_upload, str):
            # file name with extension
            file_name = os.path.basename(to_upload)

            # magic binary might not be installed on some OSes
            try:
                file_mime = magic.Magic(mime=True).from_file(to_upload)
            except Exception as e:
                print(f"Magic not working: {e}")
                print("Some OSes like Windows requires to install magic binary to work.")
                print("try: pip install py-directus[Windows]")

            # metadata
            data = {"title": title or os.path.splitext(file_name)[0] }
            if filename_download:
                data["filename_download"] = filename_download

            f = open(to_upload, 'rb')
            files = {
                "file": (file_name, f, file_mime)
            }

        elif isinstance(to_upload, UploadFile):
            # metadata
            data = {
                "title": title or os.path.splitext(to_upload.filename)[0],
            }
            if filename_download:
                data["filename_download"] = filename_download

            files = {
                "file": (to_upload.filename, BytesIO(await to_upload.read()), to_upload.content_type)
            }
        else:
            raise TypeError("The `to_upload` argument must be either a string or a `fastapi.UploadFile` instance.")

        try:
            # File
            # NOTE: CANNOT USE ASYNCHRONOUS FILES BECAUSE THEY ARE NOT SUPPORTED BY HTTPX
            # https://github.com/encode/httpx/issues/1620
            # f = await aiofiles.open(to_upload, 'rb')
            if folder_id:
                data["folder"] = folder_id
            response = await self.connection.post(url, data=data, files=files, auth=self.auth)
        finally:
            if isinstance(to_upload, str):
                f.close()

        return DirectusResponse(response)

    async def get_translations(self, clean: bool = False) -> dict[str, dict[str, str]]:
        """
        Retrieve dictionary with all translation records.

        :param clean: Returns the records grouped by `key` value when set as `True`.
        """
        items = (await self.collection(py_directus.DirectusTranslation).read()).items_as_dict()

        return parse_translations(items) if clean else items

    async def create_translations(self, *keys: Union[str, Tuple[str, str]]):
        """
        Create translation records for given keys.
        """
        # Payload
        payload = [(
                       lambda x: (
                           {"key": x, "language": "en-GB", "value": ""}
                           if isinstance(x, str) else
                           {"key": x[0], "language": x[1], "value": ""}
                       )
                   )(key) for key in keys]

        response_obj = await self.collection(py_directus.DirectusTranslation).create(payload)
        return response_obj

    async def read_settings(self) -> DirectusResponse:
        """
        Retrieve Directus settings.

        NOTE: Old logic syntax (self.collection)
        """
        collection_name = py_directus.DirectusSettings.model_config.get("collection", None)

        assert collection_name is not None

        response_obj = await DirectusRequest(self, collection_name).read(method='get')
        return response_obj

    async def update_settings(self, data: Dict[Any, Any]) -> DirectusResponse:
        """
        Change Directus settings.

        NOTE: Old logic syntax (self.collection)
        """
        collection_name = py_directus.DirectusSettings.model_config.get("collection", None)

        assert collection_name is not None

        response_obj = await DirectusRequest(self, collection_name).update(None, data)
        return response_obj

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
            user = await self.me(cache=True)
            self._user = user.item
        return self._user

    async def auth_request(self, endpoint, payload):
        url = f"{self.url}/{endpoint}"

        r = await self.connection.post(url, json=payload)
        response = DirectusResponse(r).item

        self._token = response['access_token']
        self.refresh_token = response['refresh_token']
        self.expires = response['expires']  # in milliseconds
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
        await self.clear_cache(True)

    async def start_cache(self):
        if not self._token:
            self.cache = SimpleMemoryCache("public")
        else:
            self.cache = SimpleMemoryCache(self._token)

    async def clear_cache(self, clear_all: bool = False):
        """
        Clear cache.

        :param clear_all: If set to `True`, absolutely ALL records will be deleted.
        """
        return await self.cache.clear(clear_all)

    async def logout(self) -> bool:
        url = f"{self.url}/auth/logout"
        response = await self.connection.post(url)

        self.connection.auth = None
        self._token = None
        self.refresh_token = None
        self.expires = None
        self.expiration_time = None

        # Clear cache
        if self.cache:
            await self.clear_cache(False)

        return response.status_code == 200

    async def close_connection(self):
        await self.connection.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        print("Closing connection")
        # Exception handling here
        await self.logout()
        await self.close_connection()
