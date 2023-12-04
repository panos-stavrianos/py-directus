from typing import Optional

from pydantic import ConfigDict

from .base import DirectusModel


class Role(DirectusModel):
    """
    Directus role model.
    """

    id: Optional[str] = None
    name: Optional[str] = None

    model_config = ConfigDict(collection="directus_roles")


class User(DirectusModel):
    """
    Directus user model.
    """

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

    model_config = ConfigDict(collection="directus_users")
