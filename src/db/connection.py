"""
src/db/connection.py
Singleton psycopg2 ThreadedConnectionPool.

The pool is initialised once (lazily on first use) and shared across all
requests inside the same process.  Each caller gets a connection via the
``get_connection()`` context manager, which automatically returns it to the
pool on exit.

Usage::

    from src.db.connection import get_connection

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
"""
from __future__ import annotations

import threading
from contextlib import contextmanager
from typing import Generator

import psycopg2
from psycopg2 import pool

from src.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER

_pool: pool.ThreadedConnectionPool | None = None
_pool_lock = threading.Lock()

_MIN_CONN = 1
_MAX_CONN = 10


def _get_pool() -> pool.ThreadedConnectionPool:
    """Return the singleton connection pool, creating it if necessary."""
    global _pool
    if _pool is not None:
        return _pool
    with _pool_lock:
        if _pool is None:
            _pool = pool.ThreadedConnectionPool(
                minconn=_MIN_CONN,
                maxconn=_MAX_CONN,
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
            )
    return _pool


@contextmanager
def get_connection() -> Generator[psycopg2.extensions.connection, None, None]:
    """
    Context manager that yields a psycopg2 connection from the pool.

    The connection is committed on clean exit and rolled back + returned on
    any exception.
    """
    conn_pool = _get_pool()
    conn = conn_pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn_pool.putconn(conn)


def close_pool() -> None:
    """Close all connections in the pool.  Call this on application shutdown."""
    global _pool
    if _pool is not None:
        _pool.closeall()
        _pool = None
