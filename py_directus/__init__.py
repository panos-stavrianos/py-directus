from typing import Type, Union, Optional

from httpx import AsyncClient

from . import models as _models
from .models.directus import *

from .filter import F
from .directus import Directus

try:
    from .fast_api.auth import HeaderAndCookieBearer
    from .fast_api.lifespan import init_directus
except ImportError:
    pass

DirectusActivity: Type['BaseDirectusActivity'] = BaseDirectusActivity
DirectusRevision: Type['BaseDirectusRevision'] = BaseDirectusRevision
DirectusRole: Type['BaseDirectusRole'] = BaseDirectusRole
DirectusRoles: Type['BaseDirectusRoles'] = BaseDirectusRoles
DirectusUser: Type['BaseDirectusUser'] = BaseDirectusUser
DirectusFile: Type['BaseDirectusFile'] = BaseDirectusFile
DirectusFolder: Type['BaseDirectusFolder'] = BaseDirectusFolder
DirectusPermission: Type['BaseDirectusPermission'] = BaseDirectusPermission
DirectusRelationSchema: Type['BaseDirectusRelationSchema'] = BaseDirectusRelationSchema
DirectusRelationMeta: Type['BaseDirectusRelationMeta'] = BaseDirectusRelationMeta
DirectusRelation: Type['BaseDirectusRelation'] = BaseDirectusRelation
DirectusSettings: Type['BaseDirectusSettings'] = BaseDirectusSettings
DirectusTranslation: Type['BaseDirectusTranslation'] = BaseDirectusTranslation
DirectusVersion: Type['BaseDirectusVersion'] = BaseDirectusVersion

cached_directus_instances = dict[str, Directus]()

directus_session: AsyncClient = AsyncClient()
directus_session.timeout = 5
directus_session.headers.update({'Cache-Control': 'no-store'})

directus_url: Union[str, None] = None
# Client with administrator access
directus_admin: Optional[Directus] = None
# Public directus
directus_public: Optional[Directus] = None

# Directus Translations
translations = dict[str, dict[str, str]]()


def rebuild_models():
    global DirectusActivity
    global DirectusRevision
    global DirectusRole
    global DirectusRoles
    global DirectusUser
    global DirectusFile
    global DirectusFolder
    global DirectusPermission
    global DirectusRelationSchema
    global DirectusRelationMeta
    global DirectusRelation
    global DirectusSettings
    global DirectusTranslation
    global DirectusVersion

    DirectusActivity.model_rebuild(raise_errors=False)
    DirectusRevision.model_rebuild(raise_errors=False)
    DirectusRole.model_rebuild(raise_errors=False)
    DirectusUser.model_rebuild(raise_errors=False)
    DirectusFile.model_rebuild(raise_errors=False)
    DirectusFolder.model_rebuild(raise_errors=False)
    DirectusPermission.model_rebuild(raise_errors=False)
    DirectusRelationSchema.model_rebuild(raise_errors=False)
    DirectusRelationMeta.model_rebuild(raise_errors=False)
    DirectusRelation.model_rebuild(raise_errors=False)
    DirectusSettings.model_rebuild(raise_errors=False)
    DirectusTranslation.model_rebuild(raise_errors=False)
    DirectusVersion.model_rebuild(raise_errors=False)


def setup_models(directus_models: Type['BaseDirectusModels'] = BaseDirectusModels):
    global DirectusActivity
    global DirectusRevision
    global DirectusRole
    global DirectusRoles
    global DirectusUser
    global DirectusFile
    global DirectusFolder
    global DirectusPermission
    global DirectusRelationSchema
    global DirectusRelationMeta
    global DirectusRelation
    global DirectusSettings
    global DirectusTranslation
    global DirectusVersion

    DirectusActivity = _models.directus_model_settings.DirectusActivity = directus_models.DirectusActivity if hasattr(
        directus_models,
        'DirectusActivity') else BaseDirectusActivity
    DirectusRevision = _models.directus_model_settings.DirectusRevision = directus_models.DirectusRevision if hasattr(
        directus_models,
        'DirectusRevision') else BaseDirectusRevision
    DirectusRole = _models.directus_model_settings.DirectusRole = directus_models.DirectusRole if hasattr(
        directus_models,
        'DirectusRole') else BaseDirectusRole
    DirectusRoles = _models.directus_model_settings.DirectusRoles = directus_models.DirectusRoles if hasattr(
        directus_models,
        'DirectusRoles') else BaseDirectusRoles
    DirectusUser = _models.directus_model_settings.DirectusUser = directus_models.DirectusUser if hasattr(
        directus_models,
        'DirectusUser') else BaseDirectusUser
    DirectusFile = _models.directus_model_settings.DirectusFile = directus_models.DirectusFile if hasattr(
        directus_models,
        'DirectusFile') else BaseDirectusFile
    DirectusFolder = _models.directus_model_settings.DirectusFolder = directus_models.DirectusFolder if hasattr(
        directus_models,
        'DirectusFolder') else BaseDirectusFolder
    DirectusPermission = _models.directus_model_settings.DirectusPermission = directus_models.DirectusPermission if hasattr(
        directus_models,
        'DirectusPermission') else BaseDirectusPermission
    DirectusRelationSchema = _models.directus_model_settings.DirectusRelationSchema = directus_models.DirectusRelationSchema if hasattr(
        directus_models,
        'DirectusRelationSchema') else BaseDirectusRelationSchema
    DirectusRelationMeta = _models.directus_model_settings.DirectusRelationMeta = directus_models.DirectusRelationMeta if hasattr(
        directus_models,
        'DirectusRelationMeta') else BaseDirectusRelationMeta
    DirectusRelation = _models.directus_model_settings.DirectusRelation = directus_models.DirectusRelation if hasattr(
        directus_models,
        'DirectusRelation') else BaseDirectusRelation
    DirectusSettings = _models.directus_model_settings.DirectusSettings = directus_models.DirectusSettings if hasattr(
        directus_models,
        'DirectusSettings') else BaseDirectusSettings
    DirectusTranslation = _models.directus_model_settings.DirectusTranslation = directus_models.DirectusTranslation if hasattr(
        directus_models,
        'DirectusTranslation') else BaseDirectusTranslation
    DirectusVersion = _models.directus_model_settings.DirectusVersion = directus_models.DirectusVersion if hasattr(
        directus_models,
        'DirectusVersion') else BaseDirectusVersion

    rebuild_models()


async def async_init(directus_base_url: str, directus_admin_token: str = None, 
                     directus_models: Type[BaseDirectusModels] = BaseDirectusModels, 
                     load_translations: bool = False):
    global directus_admin
    global directus_public
    global directus_url

    global translations

    # Setup defaults
    setup_models(directus_models)

    directus_url = directus_base_url
    directus_public = await Directus(directus_url, connection=directus_session)

    if directus_admin_token:
        directus_admin = await Directus(directus_url, token=directus_admin_token, connection=directus_session)

    # Load Directus translations at startup
    if load_translations:
        translations = await directus_public.get_translations(clean=True)


rebuild_models()
