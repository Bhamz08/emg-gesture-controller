"""Cutting a labeled recording into windows, and balancing the classes."""

import numpy as np

from emg.config import STEP, WIN
from emg.features import features


def window_ends(labels: np.ndarray, gesture_ids, win: int = WIN, step: int = STEP) -> np.ndarray:
    """End index (exclusive) of every window that is entirely one of the wanted gestures."""
    ends = []
    for end in range(win, len(labels) + 1, step):
        lab = labels[end - win:end]
        if lab.min() != lab.max():      # gesture changes inside the window
            continue
        if lab[0] not in gesture_ids:   # a gesture we're not using
            continue
        ends.append(end)
    return np.array(ends, dtype=int)


def cut_windows(emg, labels, reps, thresh, gesture_ids, win: int = WIN, step: int = STEP):
    """Return X (windows x features), y (gesture number) and groups (repetition number)."""
    ends = window_ends(labels, gesture_ids, win, step)
    if len(ends) == 0:
        raise ValueError("no usable windows: check gesture numbers and labels")
    X = np.array([features(emg[e - win:e], thresh) for e in ends])
    y = labels[ends - 1]
    groups = reps[ends - 1]
    return X, y, groups


def balance_rest(y: np.ndarray, seed: int = 0) -> np.ndarray:
    """Indices to keep so rest has no more windows than the biggest gesture."""
    rng = np.random.default_rng(seed)
    biggest = max(int((y == k).sum()) for k in np.unique(y) if k != 0)
    rest_idx = np.flatnonzero(y == 0)
    if len(rest_idx) <= biggest:
        return np.arange(len(y))
    drop = rng.choice(rest_idx, len(rest_idx) - biggest, replace=False)
    return np.setdiff1d(np.arange(len(y)), drop)
