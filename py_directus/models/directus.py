from typing import Optional

from .base import DirectusModel


class Role(DirectusModel):
    id: Optional[str] = None
    name: Optional[str] = None

    class Config:
        collection = "directus_roles"


class User(DirectusModel):
    id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar: Optional[str] = None
    description: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] | Optional[Role] = None
    status: Optional[str] = None
    title: Optional[str] = None
    token: Optional[str] = None

    class Config:
        collection = "directus_users"
