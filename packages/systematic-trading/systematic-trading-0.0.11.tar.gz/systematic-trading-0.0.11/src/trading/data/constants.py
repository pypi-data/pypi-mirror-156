"""
Definition of the constants of the module
"""
from methodtools import lru_cache

from .client import Client, LAST_MODIFIED as last_modified

EMPTY = "empty"

FUTURE_TYPE = "Future"


@lru_cache()
def get_futures():
    """
    Get the futures.
    """
    futures, _ = Client().get_tickers()
    return futures


LAST_MODIFIED = last_modified

LETTERS = ["F", "G", "H", "J", "K", "M", "N", "Q", "U", "V", "X", "Z"]

LIBOR_BEFORE_2001 = 6.65125
