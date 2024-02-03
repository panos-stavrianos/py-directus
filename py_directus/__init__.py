try:  # hacky way to avoid circular import after pycharm formatting
    from .models import BaseDirectusUser, BaseDirectusRole
except ImportError:
    pass

from .directus import Directus
from .filter import F

try:
    from .fast_api.auth import HeaderAndCookieBearer
    from .fast_api.lifespan import init_directus
except ImportError:
    pass

from typing import Optional, Type, Union

from httpx import AsyncClient

cached_directus_instances = dict[str, Directus]()

directus_session: AsyncClient = AsyncClient()
directus_session.timeout = 5
directus_session.headers.update({'Cache-Control': 'no-store'})

directus_url: Union[str, None] = None
# Client with administrator access
directus_admin: Optional[Directus] = None
# Public directus
directus_public: Optional[Directus] = None

DirectusUser: Type[BaseDirectusUser] = BaseDirectusUser
DirectusRole: Type[BaseDirectusRole] = BaseDirectusRole


async def async_init(directus_base_url: str, directus_admin_token: str = None,
                     directus_user_model: Type[BaseDirectusUser] = BaseDirectusUser,
                     directus_role_model: Type[BaseDirectusRole] = BaseDirectusRole,
                     ):
    global directus_admin
    global directus_public
    global directus_url
    global DirectusUser
    global DirectusRole

    DirectusUser = directus_user_model
    DirectusRole = directus_role_model

    directus_url = directus_base_url
    directus_public = await Directus(directus_url, connection=directus_session)

    if directus_admin_token:
        directus_admin = await Directus(directus_url, token=directus_admin_token, connection=directus_session)
