# Based on the cache implementation in Zeep: https://github.com/mvantellingen/python-zeep/blob/4.2.1/src/zeep/cache.py
import base64
import logging
from abc import ABC, abstractmethod
from typing import Dict, Tuple, Union, Optional
from datetime import datetime, timedelta, timezone

from py_directus.utils import get_random_string


logger = logging.getLogger(__name__)


class Base(ABC):
    """
    Base class for caching backends.
    """

    @abstractmethod
    async def add(self, query, content):
        raise NotImplementedError()

    @abstractmethod
    async def get(self, query):
        raise NotImplementedError()

    @abstractmethod
    async def delete(self, query):
        raise NotImplementedError()

    @abstractmethod
    async def clear(self, select_all):
        raise NotImplementedError()


class SimpleMemoryCache(Base):
    """
    Simple in-memory caching using dict lookup with support for timeouts
    """

    # cache persistent throughout class instances, thread-safe by default
    _cache: Dict[str, Tuple[datetime, Union[str, bytes]]] = {}

    def __init__(self, unique_id: str, timeout: int=3600):
        self._timeout = timeout

        self.unique_id = unique_id

    async def add(self, query: str, content: Union[str, bytes]):
        q_key = self._get_query_key(query)

        logger.debug("Caching contents of %s", q_key)

        if not isinstance(content, (str, bytes)):
            raise TypeError(
                "a bytes-like object is required, not {}".format(type(content).__name__)
            )

        self._cache[q_key] = (datetime.utcnow(), content)
        return True

    async def get(self, query: str):
        q_key = self._get_query_key(query)

        try:
            created, content = self._cache[q_key]
        except KeyError:
            pass
        else:
            if _is_expired(created, self._timeout):
                self._delete(q_key)
            else:
                logger.debug("Cache HIT for %s", q_key)

                return content

        logger.debug(f"Cache MISS for {q_key}")

        return None

    async def delete(self, query: str):
        q_key = self._get_query_key(query)

        d_res = self._delete(q_key)

        logger.debug(f"Deleted contents of {q_key}")

        return d_res

    async def clear(self, select_all: bool=False):
        if select_all:
            self._cache.clear()
        else:
            for key in list(self._cache):
                if key.startswith(self.unique_id):
                    self._delete(key)
        
        logger.debug(f"Cleared cache ({select_all})")

        return True

    def _delete(self, q_key: str):
        if self._cache.pop(q_key, None) is not None:
            return True
        return False

    # NOTE: Deprecated
    # def _get_unique_id(self) -> str:
    #     """
    #     Expose the version prefix to be used in content serialization.
    #     """
    #     length = 25
    #     retries = 25

    #     is_unique = False
    #     unique_id = None

    #     while retries > 0:
    #         unique_id = get_random_string(length)

    #         if unique_id not in self._cache:
    #             is_unique = True
    #             break

    #         retries -= 1

    #     # In case there was no spare id
    #     if not is_unique:
    #         raise Exception(f"No unique id could be found within the specified {retries} retries")

    #     return unique_id

    def _get_query_key(self, query: str) -> str:
        """
        Expose the version prefix to be used in content serialization.
        """
        q_key = base64.b64encode(query.encode('utf-8'))

        prefix = f"{self.unique_id}:{q_key.decode('utf-8')}"
        return prefix


def _is_expired(value: datetime, timeout: int) -> bool:
    """
    Return boolean if the value is expired

    timeout: Number of seconds after which the value is considered expired
    """
    if timeout is None:
        return False

    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    max_age = value.replace(tzinfo=timezone.utc)
    max_age += timedelta(seconds=timeout)
    return now > max_age
