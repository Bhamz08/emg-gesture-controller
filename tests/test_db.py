import sqlite3

import numpy as np
import pytest

from emg import db


@pytest.fixture
def conn(tmp_path):
    c = db.connect(tmp_path / "test.db")
    yield c
    c.close()


def test_save_and_load_calibration_windows(conn):
    user = db.get_or_create_user(conn, "anuj")
    session = db.start_session(conn, user, "calibration")
    X = np.arange(30, dtype=float).reshape(3, 10)
    db.save_windows(conn, session, [0, 50, 100], ["rest", "fist", "fist"], [1, 1, 2], X)
    db.end_session(conn, session)

    X2, gestures, reps, sessions = db.load_windows(conn, user)
    assert np.array_equal(X, X2)
    assert list(gestures) == ["rest", "fist", "fist"]
    assert list(reps) == [1, 1, 2]
    assert set(sessions) == {session}


def test_same_user_name_returns_same_id(conn):
    assert db.get_or_create_user(conn, "anuj") == db.get_or_create_user(conn, "anuj")


def test_foreign_keys_are_enforced(conn):
    with pytest.raises(sqlite3.IntegrityError):
        db.start_session(conn, user_id=999, kind="live")


def test_unknown_session_kind_is_rejected(conn):
    user = db.get_or_create_user(conn, "anuj")
    with pytest.raises(sqlite3.IntegrityError):
        db.start_session(conn, user, "nap")


def test_wrong_feature_count_fails_fast(conn):
    user = db.get_or_create_user(conn, "anuj")
    session = db.start_session(conn, user, "calibration")
    with pytest.raises(ValueError):
        db.save_windows(conn, session, [0], ["rest"], [1], np.zeros((1, 9)))
