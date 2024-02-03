from typing import Optional, Union

from .base import DirectusModel, DirectusConfigDict


class BaseDirectusRole(DirectusModel):
    """
    Directus role model.
    """
    model_config = DirectusConfigDict(collection="directus_roles")

    id: Optional[str] = None
    name: Optional[str] = None


class BaseDirectusUser(DirectusModel):
    """
    Directus user model.
    """
    model_config = DirectusConfigDict(collection="directus_users")

    id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar: Optional[str] = None
    description: Optional[str] = None
    email: Optional[str] = None
    role: Union[Optional[str], Optional[BaseDirectusRole]] = None
    status: Optional[str] = None
    title: Optional[str] = None
    token: Optional[str] = None
