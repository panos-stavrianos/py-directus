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
    """
    Rebuild globally referenced models.
    """
    global_var_names = [
        'DirectusActivity', 
        'DirectusRevision', 
        'DirectusRole', 
        # 'DirectusRoles', 
        'DirectusUser', 
        'DirectusFile', 
        'DirectusFolder', 
        'DirectusPermission', 
        'DirectusRelationSchema', 
        'DirectusRelationMeta', 
        'DirectusRelation', 
        'DirectusSettings', 
        'DirectusTranslation', 
        'DirectusVersion'
    ]

    globals_ref = globals()

    for var_name in global_var_names:
        globals_ref[var_name].model_rebuild(raise_errors=False)


def setup_models(directus_models: Type['BaseDirectusModels'] = BaseDirectusModels):
    """
    Assign globally referenced models.
    """
    global_var_names = [
        'DirectusActivity',
        'DirectusRevision',
        'DirectusRole',
        'DirectusRoles',
        'DirectusUser',
        'DirectusFile',
        'DirectusFolder',
        'DirectusPermission',
        'DirectusRelationSchema',
        'DirectusRelationMeta',
        'DirectusRelation',
        'DirectusSettings',
        'DirectusTranslation',
        'DirectusVersion'
    ]

    globals_ref = globals()

    for var_name in global_var_names:
        setattr(
            _models.directus_model_settings, var_name, (
                getattr(directus_models, var_name, None) or globals_ref[f"Base{var_name}"]
            )
        )
        globals_ref[var_name] = getattr(_models.directus_model_settings, var_name, globals_ref[f"Base{var_name}"])

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
