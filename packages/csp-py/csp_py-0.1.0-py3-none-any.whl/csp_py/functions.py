"""functions.py contains example functions for creating Runners."""

import hashlib
import urllib.request
from typing import Tuple
from urllib.error import HTTPError


def replace(s: str) -> str:
    """replace replaces uppercase vowels with other uppercase vowels."""
    return s.translate(str.maketrans("AEIOU", "UOIEA"))


def get_url(url: str) -> Tuple[str, bytes]:
    """get_url fetches a URL and returns its body."""
    try:
        with urllib.request.urlopen(url) as response:
            body = response.read()
    except HTTPError as err:
        body = str(err).encode(encoding="utf8")
    finally:
        return url, body


def hash(url: str, contents: bytes) -> Tuple[str, str]:
    """hash hashes the contents using SHA512."""
    return url, hashlib.sha512(contents).hexdigest()
