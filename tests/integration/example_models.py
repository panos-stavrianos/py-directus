from typing import Optional

from py_directus import BaseDirectusUser, BaseDirectusRole


class User(BaseDirectusUser):
    pet: Optional[str] = None


class Role2(BaseDirectusRole):
    overlord: Optional[bool] = None


class DirectusModels:
    DirectusUser = User
    DirectusRole = Role2
