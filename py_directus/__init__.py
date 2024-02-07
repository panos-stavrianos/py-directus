from typing import Type

from httpx import AsyncClient

from . import models as _models
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


def setup_models(directus_models: Type[BaseDirectusModels] = BaseDirectusModels):
    global DirectusActivity
    global DirectusRevision
    global DirectusRole
    global DirectusRoles
    global DirectusUser
    global DirectusFile
    global DirectusFolder
    global DirectusVersion

    DirectusActivity = _models.directus_model_settings.DirectusActivity = directus_models.DirectusActivity if hasattr(
        directus_models,
        'DirectusActivity') else BaseDirectusVersion
    DirectusRevision = _models.directus_model_settings.DirectusRevision = directus_models.DirectusRevision if hasattr(
        directus_models,
        'DirectusRevision') else BaseDirectusVersion
    DirectusRole = _models.directus_model_settings.DirectusRole = directus_models.DirectusRole if hasattr(
        directus_models,
        'DirectusRole') else BaseDirectusVersion
    DirectusRoles = _models.directus_model_settings.DirectusRoles = directus_models.DirectusRoles if hasattr(
        directus_models,
        'DirectusRoles') else BaseDirectusVersion
    DirectusUser = _models.directus_model_settings.DirectusUser = directus_models.DirectusUser if hasattr(
        directus_models,
        'DirectusUser') else BaseDirectusVersion
    DirectusFile = _models.directus_model_settings.DirectusFile = directus_models.DirectusFile if hasattr(
        directus_models,
        'DirectusFile') else BaseDirectusVersion
    DirectusFolder = _models.directus_model_settings.DirectusFolder = directus_models.DirectusFolder if hasattr(
        directus_models,
        'DirectusFolder') else BaseDirectusVersion
    DirectusVersion = _models.directus_model_settings.DirectusVersion = directus_models.DirectusVersion if hasattr(
        directus_models,
        'DirectusVersion') else BaseDirectusVersion

    DirectusActivity.model_rebuild(raise_errors=False)
    DirectusRevision.model_rebuild(raise_errors=False)
    DirectusRole.model_rebuild(raise_errors=False)
    DirectusUser.model_rebuild(raise_errors=False)
    DirectusFile.model_rebuild(raise_errors=False)
    DirectusFolder.model_rebuild(raise_errors=False)
    DirectusVersion.model_rebuild(raise_errors=False)


async def async_init(directus_base_url: str, directus_admin_token: str = None,
                     load_translations: bool = False,
                     directus_models: Type[BaseDirectusModels] = BaseDirectusModels):
    global directus_admin
    global directus_public
    global directus_url

    global translations

    setup_models(directus_models)

    directus_url = directus_base_url
    directus_public = await Directus(directus_url, connection=directus_session)

    if directus_admin_token:
        directus_admin = await Directus(directus_url, token=directus_admin_token, connection=directus_session)

    # if load_translations:
    #     translations = await directus_public.get_translations()# TODO
