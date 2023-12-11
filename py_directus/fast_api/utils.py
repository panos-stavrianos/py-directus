import asyncio
from enum import Enum
from typing import Union, Optional, List

from py_directus.models import Role
from py_directus import Directus
from py_directus.fast_api import globals


async def get_directus_login(email: str, password: str) -> Directus:
    d = await Directus(globals.directus_url, connection=globals.directus_session, email=email, password=password)
    globals.cached_directus_instances[d.token] = d
    return d


async def get_directus_from_token(access_token, refresh_token=None) -> Optional[Directus]:
    directus = await Directus(globals.directus_url, token=access_token, refresh_token=refresh_token,
                              connection=globals.directus_session)
    await directus.user  # noqa
    return directus


async def directus_logout(directus: Directus):
    globals.cached_directus_instances.pop(directus.token, None)
    await directus.logout()


class Roles(str, Enum):
    ADMIN = "Administrator"
    COMPANY = "Company"
    LICENSE = "License"
    CREDIT = "Credit"
    DEVICE = "Device"
    PARTNER = "Partner"


class RoleToID:
    def __init__(self):
        self.roles: Optional[List[Role]] = None

    def __await__(self):
        async def closure():
            if getattr(self, "roles", None) is None:
                # Perform login manually, because the global was instantiated without awaiting
                await globals.directus_admin
                roles = await globals.directus_admin.collection(Role).read()
                self.roles = {role.name: role.id for role in roles.items}
            return self

        return closure().__await__()

    def __call__(self, role: Union[str, Roles]) -> [str]:  # noqa
        if isinstance(role, Roles):
            role = role.value
        return [self.roles[role]]


role_to_id = RoleToID()
