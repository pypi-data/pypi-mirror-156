from typing import Optional
import atexit
import copy
import functools
import requests
import zstandard

import sqlite3 as sql

from snail_dict import conf


conf.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
DB = sql.connect(str(conf.DB_PATH), check_same_thread=False)

atexit.register(lambda: DB.commit() or DB.close())


__all__ = ["memcached", "sqlite_cached"]


def memcached(func):
    cache = {}

    def wrapper(key):
        if key in cache:
            return copy.deepcopy(cache[key])

        val = func(key)
        if val is not None:
            cache[key] = val

        return val

    return wrapper


def _identity(v):
    return v


def sqlite_cached(table_name: str, to_bytes=_identity, from_bytes=_identity):
    _create_table(table_name)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(key):
            v_bytes = _value_from_db(table_name, key)
            if v_bytes:
                return from_bytes(v_bytes)

            v = func(key)
            if v is None:
                return None

            _set_value_to_db(table_name, key, to_bytes(v))
            return v

        return wrapper

    return decorator


def _create_table(table_name):
    DB.execute(
        f"CREATE TABLE IF NOT EXISTS {table_name} " "(key TEXT PRIMARY KEY,value BLOB);"
    )
    DB.commit()


def _value_from_db(table_name: str, key: str) -> Optional[bytes]:
    row = DB.execute(f"SELECT value FROM {table_name} WHERE key=?", (key,)).fetchone()
    if row is not None:
        return row[0]
    else:
        return None


def _set_value_to_db(table_name: str, key: str, value: bytes):
    DB.execute(
        f"INSERT OR IGNORE INTO {table_name} (key, value) VALUES (?,?);",
        (key, value),
    )
    DB.commit()


class CachedWebSession:
    UA = "Mozilla/5.0 (X11; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0"
    HEADER = {
        "User-agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }

    def __init__(self) -> None:
        self.session = requests.Session()
        self.get_content = memcached(
            sqlite_cached(
                "webcache",
                to_bytes=lambda b: zstandard.compress(b),
                from_bytes=lambda b: zstandard.decompress(b).decode(),
            )(self._get_content)
        )

    def _get_content(self, url: str) -> bytes:
        response = self.session.get(url, headers=self.HEADER)
        print(response.history)
        response.raise_for_status()
        return response.content
