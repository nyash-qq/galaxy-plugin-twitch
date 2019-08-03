import logging
import os
import sqlite3
from contextlib import contextmanager
from typing import Dict, List, Optional


@contextmanager
def _db_connect(db_path: str):
    db = sqlite3.connect("file:{db_path}?mode=ro".format(db_path=db_path), uri=True)
    try:
        yield db

    finally:
        db.close()


@contextmanager
def _db_cursor(db):
    cursor = db.cursor()
    try:
        yield cursor

    finally:
        cursor.close()


def db_select(db_path: str, query: str) -> Optional[List[Dict]]:
    if not os.path.exists(db_path):
        raise FileNotFoundError("DB {db} does not exists".format(db=db_path))

    with _db_connect(db_path=db_path) as db:
        with _db_cursor(db=db) as cursor:
            res = cursor.execute(query).fetchall()
            column_names = [column[0] for column in cursor.description]
            return [dict(zip(column_names, row)) for row in res]


def get_cookie(db_cookies_path: str, cookie_name: str) -> Optional[str]:
    try:
        return db_select(
            db_path=db_cookies_path
            , query="select value from cookies where name='{cookie}';".format(cookie=cookie_name)
        )[0]["value"]

    except Exception:
        logging.exception("Failed to get a cookie: '{cookie}'".format(cookie=cookie_name))
        return None
