from enum import Enum
from typing import Union, Optional, List

import py_directus
from py_directus import Directus


async def get_directus_login(email: str, password: str) -> Directus:
    d = await Directus(py_directus.directus_url, connection=py_directus.directus_session, email=email,
                       password=password)
    py_directus.cached_directus_instances[d.token] = d
    return d


async def get_directus_from_token(access_token, refresh_token=None) -> Optional[Directus]:
    directus = await Directus(py_directus.directus_url, token=access_token, refresh_token=refresh_token,
                              connection=py_directus.directus_session)
    await directus.user  # noqa
    return directus


async def directus_logout(directus: Directus):
    py_directus.cached_directus_instances.pop(directus.token, None)
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
        self.roles: Optional[List[py_directus.DirectusRole]] = None

    def __await__(self):
        async def closure():
            if getattr(self, "roles", None) is None:
                # Perform login manually, because the global was instantiated without awaiting
                await py_directus.directus_admin
                roles = await py_directus.directus_admin.collection(py_directus.DirectusRole).read()
                self.roles = {role.name: role.id for role in roles.items}
            return self

        return closure().__await__()

    def __call__(self, role: Union[str, Roles]) -> [str]:  # noqa
        if isinstance(role, Roles):
            role = role.value
        return [self.roles[role]]


role_to_id = RoleToID()
