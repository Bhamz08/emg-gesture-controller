"""SQLite database: users, sessions, windows, models, actions and prompts."""

import sqlite3
import time
from pathlib import Path

import numpy as np

from emg.config import FEATURE_NAMES

SCHEMA = f"""
CREATE TABLE IF NOT EXISTS users (
  id         INTEGER PRIMARY KEY,
  name       TEXT NOT NULL UNIQUE,
  created_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
  id         INTEGER PRIMARY KEY,
  user_id    INTEGER NOT NULL REFERENCES users(id),
  kind       TEXT NOT NULL CHECK (kind IN ('calibration', 'live', 'typing_test', 'prompt_test')),
  started_at REAL NOT NULL,
  ended_at   REAL,
  raw_file   TEXT,
  notes      TEXT
);

CREATE TABLE IF NOT EXISTS windows (
  id         INTEGER PRIMARY KEY,
  session_id INTEGER NOT NULL REFERENCES sessions(id),
  t_ms       INTEGER NOT NULL,
  gesture    TEXT NOT NULL,
  repetition INTEGER NOT NULL,
  {", ".join(f"{name} REAL" for name in FEATURE_NAMES)}
);

CREATE TABLE IF NOT EXISTS models (
  id          INTEGER PRIMARY KEY,
  user_id     INTEGER NOT NULL REFERENCES users(id),
  created_at  REAL NOT NULL,
  algorithm   TEXT NOT NULL,
  n_sessions  INTEGER NOT NULL,
  cv_accuracy REAL NOT NULL,
  file_path   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS actions (
  id         INTEGER PRIMARY KEY,
  session_id INTEGER NOT NULL REFERENCES sessions(id),
  model_id   INTEGER NOT NULL REFERENCES models(id),
  ts         REAL NOT NULL,
  gesture    TEXT NOT NULL,
  confidence REAL NOT NULL,
  mistake    INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS prompts (
  id         INTEGER PRIMARY KEY,
  session_id INTEGER NOT NULL REFERENCES sessions(id),
  ts         REAL NOT NULL,
  expected   TEXT NOT NULL,
  action_id  INTEGER REFERENCES actions(id),
  latency_ms REAL
);
"""


def connect(path) -> sqlite3.Connection:
    """Open (or create) the database, with foreign keys enforced."""
    conn = sqlite3.connect(Path(path))
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(SCHEMA)
    return conn


def get_or_create_user(conn, name: str) -> int:
    row = conn.execute("SELECT id FROM users WHERE name = ?", (name,)).fetchone()
    if row:
        return row[0]
    cur = conn.execute("INSERT INTO users (name, created_at) VALUES (?, ?)", (name, time.time()))
    conn.commit()
    return cur.lastrowid


def start_session(conn, user_id: int, kind: str, raw_file=None, notes=None) -> int:
    cur = conn.execute(
        "INSERT INTO sessions (user_id, kind, started_at, raw_file, notes) VALUES (?, ?, ?, ?, ?)",
        (user_id, kind, time.time(), raw_file, notes),
    )
    conn.commit()
    return cur.lastrowid


def end_session(conn, session_id: int) -> None:
    conn.execute("UPDATE sessions SET ended_at = ? WHERE id = ?", (time.time(), session_id))
    conn.commit()


def save_windows(conn, session_id: int, t_ms, gestures, reps, X) -> None:
    """Save labeled windows. gestures are names like 'fist'; X is (windows x 10)."""
    X = np.asarray(X, dtype=float)
    if X.shape[1] != len(FEATURE_NAMES):
        raise ValueError(f"expected {len(FEATURE_NAMES)} features, got {X.shape[1]}")
    cols = ", ".join(["session_id", "t_ms", "gesture", "repetition", *FEATURE_NAMES])
    marks = ", ".join(["?"] * (4 + len(FEATURE_NAMES)))
    rows = [
        (session_id, int(t), str(g), int(r), *map(float, x))
        for t, g, r, x in zip(t_ms, gestures, reps, X)
    ]
    conn.executemany(f"INSERT INTO windows ({cols}) VALUES ({marks})", rows)
    conn.commit()


def load_windows(conn, user_id: int):
    """All calibration windows for a user: X, gesture names, repetitions, session ids."""
    rows = conn.execute(
        f"""
        SELECT w.{", w.".join(FEATURE_NAMES)}, w.gesture, w.repetition, w.session_id
        FROM windows w
        JOIN sessions s ON s.id = w.session_id
        WHERE s.user_id = ? AND s.kind = 'calibration'
        ORDER BY w.id
        """,
        (user_id,),
    ).fetchall()
    n = len(FEATURE_NAMES)
    X = np.array([r[:n] for r in rows], dtype=float).reshape(-1, n)
    gestures = np.array([r[n] for r in rows])
    reps = np.array([r[n + 1] for r in rows], dtype=int)
    sessions = np.array([r[n + 2] for r in rows], dtype=int)
    return X, gestures, reps, sessions


def save_model(conn, user_id: int, algorithm: str, n_sessions: int, cv_accuracy: float, file_path) -> int:
    cur = conn.execute(
        "INSERT INTO models (user_id, created_at, algorithm, n_sessions, cv_accuracy, file_path) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, time.time(), algorithm, n_sessions, cv_accuracy, str(file_path)),
    )
    conn.commit()
    return cur.lastrowid
