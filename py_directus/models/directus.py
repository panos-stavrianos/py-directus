from __future__ import annotations

from enum import Enum
from typing import Optional, Union, List, Pattern

from pydantic import Json
from pydantic.main import BaseModel

from .base import DirectusModel, DirectusConfigDict
from .types import ModelDateTime

__all__ = [
    'BaseDirectusActivity',
    'BaseDirectusRevision',
    'BaseDirectusRoles',
    'BaseDirectusRole',
    'BaseDirectusUser',
    'BaseDirectusFile',
    'BaseDirectusFolder',
    'BaseDirectusPermission',
    'BaseDirectusRelationSchema',
    'BaseDirectusRelationMeta',
    'BaseDirectusRelation',
    'BaseDirectusSettings',
    'BaseDirectusTranslation',
    'BaseDirectusVersion',
    'BaseDirectusModels',
    'directus_model_settings'
]


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


class BaseDirectusPermission(DirectusModel):
    """
    Directus permission model.
    """
    model_config = DirectusConfigDict(collection="directus_permissions")

    id: Optional[str] = None
    role: Optional[Union[str, 'directus_model_settings.DirectusRole']] = None
    collection: Optional[str] = None
    action: Optional[str] = None
    permissions: Optional[dict] = None
    validation: Optional[dict] = None
    presets: Optional[dict] = None
    fields: Optional[List[str]] = None


class BaseDirectusRelationSchema(BaseModel):
    """
    Schema model for the relation model.
    """
    table: Optional[str] = None
    column: Optional[str] = None
    foreign_key_table: Optional[str] = None
    foreign_key_column: Optional[str] = None
    constraint_name: Optional[str] = None
    on_update: Optional[str] = None
    on_delete: Optional[str] = None


class BaseDirectusRelationMeta(BaseModel):
    """
    Meta model for the relation model.
    """
    id: Optional[int] = None
    junction_field: Optional[str] = None
    many_collection: Optional[str] = None
    many_field: Optional[str] = None
    one_allowed_collections: Optional[str] = None
    one_collection: Optional[str] = None
    one_collection_field: Optional[str] = None
    one_deselect_action: Optional[str] = None
    one_field: Optional[str] = None
    sort_field: Optional[str] = None


class BaseDirectusRelation(DirectusModel):
    """
    Directus relation model.
    """
    model_config = DirectusConfigDict(collection="directus_relations")

    collection: Optional[str] = None
    field: Optional[str] = None
    related_collection: Optional[str] = None
    schema: Optional['directus_model_settings.DirectusRelationSchema'] = None
    meta: Optional['directus_model_settings.DirectusRelationMeta'] = None


class BaseDirectusSettings(DirectusModel):
    """
    Directus settings model.
    """
    model_config = DirectusConfigDict(collection="directus_settings")

    id: Optional[str] = None
    project_name: Optional[str] = None
    project_descriptor: Optional[str] = None
    project_url: Optional[str] = None
    project_color: Optional[str] = None
    project_logo: Optional[Union[str, 'directus_model_settings.DirectusFile']] = None
    public_foreground: Optional[Union[str, 'directus_model_settings.DirectusFile']] = None
    public_background: Optional[Union[str, 'directus_model_settings.DirectusFile']] = None
    public_favicon: Optional[Union[str, 'directus_model_settings.DirectusFile']] = None
    public_note: Optional[str] = None
    default_appearance: Optional[str] = None
    default_theme_light: Optional[str] = None
    default_theme_dark: Optional[str] = None
    theme_light_overrides: Optional[Json] = None
    theme_dark_overrides: Optional[Json] = None
    auth_login_attempts: Optional[int] = None
    auth_password_policy: Optional[Pattern] = None
    storage_asset_transform: Optional[str] = None
    storage_asset_presets: Optional[List[dict]] = None
    custom_css: Optional[str] = None
    storage_default_folder: Optional[str] = None
    basemaps: Optional[List[dict]] = None
    mapbox_key: Optional[str] = None
    module_bar: Optional[List[dict]] = None
    custom_aspect_ratios: Optional[List[dict]] = None


class BaseDirectusTranslation(DirectusModel):
    """
    Directus custom translation model.
    """
    model_config = DirectusConfigDict(collection="directus_translations")

    id: Optional[str] = None
    key: Optional[str] = None
    language: Optional[str] = None
    value: Optional[str] = None


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
    DirectusPermission = BaseDirectusPermission
    DirectusRelationSchema = BaseDirectusRelationSchema
    DirectusRelationMeta = BaseDirectusRelationMeta
    DirectusRelation = BaseDirectusRelation
    DirectusSettings = BaseDirectusSettings
    DirectusTranslation = BaseDirectusTranslation
    DirectusVersion = BaseDirectusVersion


directus_model_settings = BaseDirectusModels()
