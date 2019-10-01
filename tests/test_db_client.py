from sqlite3 import OperationalError

import pytest

from twitch_db_client import db_select, get_cookie


@pytest.fixture()
def db_path_mock():
    return "db-path"


@pytest.fixture()
def db_connect_mock(db_path_mock, os_path_exists_mock, mocker):
    connect = mocker.patch("sqlite3.connect")

    yield connect

    os_path_exists_mock.assert_called_once_with(db_path_mock)
    connect.assert_called_once_with(f"file:{db_path_mock}?mode=ro", uri=True)


@pytest.fixture()
def db_cursor_mock(db_connect_mock):
    cursor = db_connect_mock.return_value.cursor
    cursor.return_value.description.return_value = (("name",), ("value",))

    yield cursor

    cursor.assert_called_once_with()


@pytest.fixture()
def db_execute_mock(db_cursor_mock):
    db_execute_mock = db_cursor_mock.return_value.execute

    yield db_execute_mock

    db_execute_mock.assert_called_once()


@pytest.fixture()
def db_query_fetchall(db_execute_mock):
    db_query_fetchall = db_execute_mock.return_value.fetchall

    yield db_query_fetchall

    db_query_fetchall.assert_called_once_with()


def test_no_db(os_path_exists_mock, invalid_path):
    with pytest.raises(FileNotFoundError):
        db_select(db_path=invalid_path, query="")

    os_path_exists_mock.assert_called_once_with(invalid_path)


def test_cannot_connect(db_connect_mock, db_path_mock):
    db_connect_mock.side_effect = OperationalError

    with pytest.raises(OperationalError):
        db_select(db_path=db_path_mock, query="")


def test_cannot_get_cursor(db_cursor_mock, db_path_mock):
    db_cursor_mock.side_effect = OperationalError

    with pytest.raises(OperationalError):
        db_select(db_path=db_path_mock, query="")


def test_invalid_query(db_execute_mock, db_path_mock):
    db_execute_mock.side_effect = OperationalError

    with pytest.raises(OperationalError):
        db_select(db_path=db_path_mock, query="select-query")


def test_select_query(db_cursor_mock, db_query_fetchall, db_path_mock):
    db_cursor_mock.return_value.description = (("name",), ("value",))
    db_query_fetchall.return_value = (("key1", "value1"), ("key2", "value2"),)

    assert db_select(db_path=db_path_mock, query="select-query") == [
        {"name": "key1", "value": "value1"}
        , {"name": "key2", "value": "value2"}
    ]


def test_failed_to_get_cookie(db_cursor_mock, db_query_fetchall, db_path_mock):
    db_cursor_mock.return_value.description = (("name",), ("value",))
    db_query_fetchall.return_value = []

    assert get_cookie(db_path_mock, "cookie") is None


def test_get_cookie(db_cursor_mock, db_query_fetchall, db_path_mock):
    db_cursor_mock.return_value.description = (("name",), ("value",))
    db_query_fetchall.return_value = (("cookie", "value"),)

    assert get_cookie(db_path_mock, "cookie") == "value"
