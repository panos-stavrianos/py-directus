from __future__ import annotations

from enum import Enum
from typing import Optional, Union, List

from .base import DirectusModel, DirectusConfigDict
from .types import ModelDateTime


class BaseDirectusActivity(DirectusModel):
    """
    Directus activity model.
    """
    model_config = DirectusConfigDict(collection="directus_activity")

    action: Optional[str] = None
    collection: Optional[str] = None
    comment: Optional[str] = None
    id: Optional[int] = None
    ip: Optional[int] = None
    item: Optional[str] = None
    timestamp: Optional[Union[str, ModelDateTime.field]] = None
    user: Optional[Union[str, 'directus_model_settings.DirectusUser']] = None
    user_agent: Optional[str] = None
    revisions: Optional[List[Union[int, 'directus_model_settings.DirectusRevision']]] = None


class BaseDirectusRevision(DirectusModel):
    """
    Directus revision model.
    """
    model_config = DirectusConfigDict(collection="directus_revisions")

    id: Optional[int] = None
    activity: Optional[Union[str, 'directus_model_settings.DirectusActivity']] = None
    collection: Optional[str] = None
    item: Optional[str] = None
    data: Optional[dict] = None
    delta: Optional[dict] = None
    parent: Optional[Union[str, 'directus_model_settings.DirectusRevision']] = None
    version: Optional[Union[str, 'directus_model_settings.DirectusVersion']] = None


class BaseDirectusRoles(str, Enum):
    ADMIN = "Administrator"


class BaseDirectusRole(DirectusModel):
    """
    Directus role model.
    """
    model_config = DirectusConfigDict(collection="directus_roles")

    id: Optional[str] = None
    name: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    users: Optional[List[Union[str, 'directus_model_settings.DirectusUser']]] = None


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
    role: Optional[Union[str, 'directus_model_settings.DirectusRole']] = None
    status: Optional[str] = None
    title: Optional[str] = None
    token: Optional[str] = None
    tags: Optional[List[str]] = None


class BaseDirectusFile(DirectusModel):
    """
    Directus file model.
    """
    model_config = DirectusConfigDict(collection="directus_files")

    id: Optional[str] = None
    storage: Optional[str] = None
    filename_disk: Optional[str] = None
    filename_download: Optional[str] = None
    title: Optional[str] = None
    type: Optional[str] = None
    folder: Optional[Union[str, 'directus_model_settings.DirectusFolder']] = None
    uploaded_by: Optional[Union[str, 'directus_model_settings.DirectusUser']] = None
    uploaded_on: Optional[ModelDateTime.field] = None
    modified_by: Optional[Union[str, 'directus_model_settings.DirectusUser']] = None
    modified_on: Optional[ModelDateTime.field] = None
    filesize: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None
    description: Optional[str] = None
    location: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None


class BaseDirectusFolder(DirectusModel):
    """
    Directus folder model.
    """
    model_config = DirectusConfigDict(collection="directus_folders")

    id: Optional[str] = None
    name: Optional[str] = None
    parent: Optional[Union[str, 'directus_model_settings.DirectusFolder']] = None


class BaseDirectusVersion(DirectusModel):
    """
    Directus version model.
    """
    model_config = DirectusConfigDict(collection="directus_versions")

    id: Optional[str] = None
    key: Optional[str] = None
    name: Optional[str] = None
    collection: Optional[str] = None
    item: Optional[str] = None
    date_created: Optional[str] = None
    user_created: Optional[Union[str, 'directus_model_settings.DirectusUser']] = None


class BaseDirectusModels:
    """
    Directus models.
    """
    DirectusActivity = BaseDirectusActivity
    DirectusRevision = BaseDirectusRevision
    DirectusRole = BaseDirectusRole
    DirectusRoles = BaseDirectusRoles
    DirectusUser = BaseDirectusUser
    DirectusFile = BaseDirectusFile
    DirectusFolder = BaseDirectusFolder
    DirectusVersion = BaseDirectusVersion


directus_model_settings = BaseDirectusModels()
