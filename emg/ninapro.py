"""Loading Ninapro DB2 files into the same shape the live system will produce."""

import glob
from pathlib import Path

import numpy as np
from scipy.io import loadmat
from scipy.signal import decimate


def fix_rest_reps(reps: np.ndarray) -> np.ndarray:
    """Give rest samples (repetition 0) the repetition of the gesture just before them.

    Rest at the very start has no gesture before it, so it gets the first repetition.
    Without this, all rest lands in one group and is tested in only one fold.
    """
    if not (reps > 0).any():
        raise ValueError("no repetition numbers above 0")
    fixed = reps.copy()
    for i in range(1, len(fixed)):
        if fixed[i] == 0:
            fixed[i] = fixed[i - 1]
    fixed[fixed == 0] = fixed[fixed > 0][0]
    return fixed


def load(path, channels):
    """Return (emg, labels, reps) at 1,000 Hz for the given 0-based electrode indices."""
    d = loadmat(Path(path))
    emg = d["emg"][:, channels].astype(float)
    labels = d["restimulus"].ravel().astype(int)
    reps = d["rerepetition"].ravel().astype(int)

    emg = decimate(emg, 2, axis=0)   # 2,000 Hz -> 1,000 Hz (filters first)
    labels = labels[::2]             # categories: just take every 2nd
    reps = fix_rest_reps(reps[::2])
    return emg, labels, reps


def expand(patterns) -> list:
    """Turn arguments like 'data/ninapro/S*_E1_A1.mat' into a sorted list of real files.

    Windows terminals don't expand '*' themselves, so the scripts do it here.
    """
    files = sorted({f for p in patterns for f in (glob.glob(p) or [p])})
    missing = [f for f in files if not Path(f).is_file()]
    if missing:
        raise FileNotFoundError(f"not found: {', '.join(missing)}")
    return files


def subject_name(path) -> str:
    """'S3_E1_A1.mat' -> 'ninapro_S3'."""
    return "ninapro_" + Path(path).stem.split("_")[0]
