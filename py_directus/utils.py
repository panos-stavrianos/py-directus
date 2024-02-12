import secrets
import itertools
from typing import Union, List

RANDOM_STRING_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def get_random_string(length=None, allowed_chars=RANDOM_STRING_CHARS):
    """
    Return a securely generated random string.

    The bit length of the returned value can be calculated with the formula:
        log_2(len(allowed_chars)^length)

    For example, with default `allowed_chars` (26+26+10), this gives:
      * length: 12, bit length =~ 71 bits
      * length: 22, bit length =~ 131 bits

    Origin: https://github.com/django/django/blob/3.2.23/django/utils/crypto.py
    """
    if length is None:
        length = 12
    return "".join(secrets.choice(allowed_chars) for i in range(length))


def parse_translations(all_translations: List[dict]) -> Union[dict[str, dict[str, str]], None]:
    if not all_translations:
        return None

    grouper = itertools.groupby(all_translations, lambda x: x['key'])

    return {
        f"{key}": {
            translation['language']: translation['value']
            for translation in group_recs
            
        } for key, group_recs in grouper
    }
