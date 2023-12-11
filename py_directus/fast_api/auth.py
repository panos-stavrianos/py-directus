import asyncio
from functools import wraps
from http import HTTPStatus
from typing import Union, Optional, List

from dotenv import load_dotenv
from httpx import AsyncClient

from fastapi import HTTPException
from fastapi.security.utils import get_authorization_scheme_param

from starlette.requests import Request
from starlette.responses import Response
from starlette.status import HTTP_307_TEMPORARY_REDIRECT

from py_directus import Directus

from .utils import (
    get_directus_from_token, 
    role_to_id
)
from .exceptions import ApiException


class HeaderAndCookieBearer:
    """
    Creates a `Directus` instance from provided credentials in request headers.
    """

    @staticmethod
    async def check_header(request: Request) -> Optional[Directus]:
        header_authorization = request.headers.get("Authorization")
        scheme, credentials = get_authorization_scheme_param(header_authorization)
        if not (header_authorization and scheme and credentials) or scheme.lower() != "bearer":
            return None
        return await get_directus_from_token(credentials)

    @staticmethod
    async def check_cookie(request: Request) -> Optional[Directus]:
        access_token: str = request.cookies.get("access_token")
        refresh_token: str = request.cookies.get("refresh_token")
        return await get_directus_from_token(access_token, refresh_token) if (access_token and refresh_token) else None

    async def __call__(self, request: Request, response: Response) -> Optional[Directus]:
        header_directus = await HeaderAndCookieBearer.check_header(request)
        cookie_directus = await HeaderAndCookieBearer.check_cookie(request)
        directus = header_directus or cookie_directus

        if directus:
            return directus

        raise HTTPException(
            status_code=HTTP_307_TEMPORARY_REDIRECT,
            headers={'Location': '/login'}
        )


directus_auth = HeaderAndCookieBearer()


def assert_role(allowed_roles: Union[str, List[str]] = None):
    def assert_role_inner(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            _allowed_roles = allowed_roles
            if isinstance(_allowed_roles, str):
                _allowed_roles = [_allowed_roles]

            await role_to_id
            roles_ids = [role_to_id(role) for role in _allowed_roles]
            roles_ids = [item for sublist in roles_ids for item in sublist]  # flatten list
            directus = None

            if "directus" in kwargs:
                directus = kwargs['directus']
            else:
                for arg in args:
                    if isinstance(arg, Directus):
                        directus = arg
                        break

            if not directus:
                raise ApiException(
                    "Not allowed, you must be authenticated", 
                    {'not_allowed': _allowed_roles},
                    HTTPStatus.FORBIDDEN
                )

            directus_user = await directus.user
            user_role = directus_user.role

            if user_role not in roles_ids:
                raise ApiException('Not allowed', {'not_allowed': _allowed_roles}, HTTPStatus.FORBIDDEN)
            if asyncio.iscoroutinefunction(func):  # check if wrapped function is a coroutine function
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)

        return wrapper

    return assert_role_inner
