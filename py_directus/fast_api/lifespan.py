import functools
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Union, Optional, Type

import py_directus as glob_vars

if TYPE_CHECKING:
    from fastapi import FastAPI


@asynccontextmanager
async def _lifespan(app: Union['FastAPI', None] = None, directus_base_url: str = None, directus_admin_token: str = None, *args, **kwargs):
    """
    Only when used directly as context manager we have access to the `FastAPI` instance through the `app` argument.
    """

    # Initialize global clients
    await glob_vars.async_init(directus_base_url, directus_admin_token)

    try:
        yield
    finally:
        # Close global clients
        if glob_vars.directus_admin:
            await glob_vars.directus_admin.logout()
        if glob_vars.directus_public:
            await glob_vars.directus_public.logout()
        if glob_vars.directus_session:
            await glob_vars.directus_session.aclose()


def lifespan(*og_args, **og_kwargs):
    def wrapper(cm=None, *ag_args, **ag_kwargs):
        if callable(cm):
            @asynccontextmanager
            @functools.wraps(cm)
            async def wrapped(*args, **kwargs):
                # NOTE: FIND A WAY TO PROVIDE THE `app` ARGUMENT TO OUR LIFESPAN
                async with _lifespan(*og_args, **og_kwargs) as og_res:
                    async with cm(*args, **kwargs) as cm_res:
                        # Occupy resources
                        try:
                            yield cm_res
                        finally:
                            # Release resources
                            pass
            return wrapped
        else:
            return _lifespan(*og_args, *ag_args, **og_kwargs, **ag_kwargs)
    return wrapper


def init_directus(app: 'FastAPI', directus_base_url: str, directus_admin_token: str):
    """
    Wrap the lifespan context manager of FastAPI with our own.
    """

    cm = app.router.lifespan_context
    app.router.lifespan_context = lifespan(
        directus_base_url=directus_base_url, 
        directus_admin_token=directus_admin_token
    )(cm)
