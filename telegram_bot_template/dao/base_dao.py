"""Base DAO class for the Telegram bot."""

import asyncpg
from typing import Optional

class BaseDAO:
    """Base class for all DAOs."""

    def __init__(self, pool: asyncpg.Pool):
        self._pool = pool