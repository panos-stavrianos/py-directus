from typing import Type

from httpx import AsyncClient

from .models.directus import *

DirectusActivity: Type[BaseDirectusActivity] = BaseDirectusActivity
DirectusRevision: Type[BaseDirectusRevision] = BaseDirectusRevision
DirectusRole: Type[BaseDirectusRole] = BaseDirectusRole
DirectusRoles: Type[BaseDirectusRoles] = BaseDirectusRoles
DirectusUser: Type[BaseDirectusUser] = BaseDirectusUser
DirectusFile: Type[BaseDirectusFile] = BaseDirectusFile
DirectusFolder: Type[BaseDirectusFolder] = BaseDirectusFolder
DirectusVersion: Type[BaseDirectusVersion] = BaseDirectusVersion

from .directus import Directus
from .filter import F

try:
    from .fast_api.auth import HeaderAndCookieBearer
    from .fast_api.lifespan import init_directus
except ImportError:
    pass

cached_directus_instances = dict[str, Directus]()

directus_session: AsyncClient = AsyncClient()
directus_session.timeout = 5
directus_session.headers.update({'Cache-Control': 'no-store'})

directus_url: Union[str, None] = None
# Client with administrator access
directus_admin: Optional[Directus] = None
# Public directus
directus_public: Optional[Directus] = None

translations = dict[str, dict[str, str]]()


async def async_init(directus_base_url: str, directus_admin_token: str = None,
                     load_translations: bool = False,
                     directus_models: Type[BaseDirectusModels] = BaseDirectusModels):
    global directus_admin
    global directus_public
    global directus_url

    global translations

    global DirectusActivity
    global DirectusRevision
    global DirectusRole
    global DirectusRoles
    global DirectusUser
    global DirectusFile
    global DirectusFolder
    global DirectusVersion

    DirectusActivity = directus_models.DirectusActivity
    DirectusRevision = directus_models.DirectusRevision
    DirectusRole = directus_models.DirectusRole
    DirectusRoles = directus_models.DirectusRoles
    DirectusUser = directus_models.DirectusUser
    DirectusFile = directus_models.DirectusFile
    DirectusFolder = directus_models.DirectusFolder
    DirectusVersion = directus_models.DirectusVersion

    directus_url = directus_base_url
    directus_public = await Directus(directus_url, connection=directus_session)

    if directus_admin_token:
        directus_admin = await Directus(directus_url, token=directus_admin_token, connection=directus_session)

    # if load_translations:
    #     translations = await directus_public.get_translations()# TODO
