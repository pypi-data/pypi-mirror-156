"""
Definition of the constants of the module
"""
from .client import Client, LAST_MODIFIED as last_modified

EMPTY = "empty"

FUTURE_TYPE = "Future"

FUTURES, _ = Client().get_tickers()

LAST_MODIFIED = last_modified

LETTERS = ["F", "G", "H", "J", "K", "M", "N", "Q", "U", "V", "X", "Z"]

LIBOR_BEFORE_2001 = 6.65125
