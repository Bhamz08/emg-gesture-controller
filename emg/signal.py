"""Filtering. The same clean() runs on Ninapro data and on live sensor data."""

import numpy as np
from scipy.signal import butter, iirnotch, lfilter

from emg.config import FS

_HP_B, _HP_A = butter(4, 20, btype="highpass", fs=FS)  # removes slow drift
_NOTCH_B, _NOTCH_A = iirnotch(60, 30, fs=FS)            # removes 60 Hz power-line hum


def clean(x: np.ndarray) -> np.ndarray:
    """Filter a (samples x channels) array. Works forward in time, like the live system."""
    if x.ndim != 2:
        raise ValueError(f"expected a 2-D array (samples x channels), got shape {x.shape}")
    x = lfilter(_HP_B, _HP_A, x, axis=0)
    return lfilter(_NOTCH_B, _NOTCH_A, x, axis=0)


def rest_noise(x: np.ndarray, labels: np.ndarray) -> np.ndarray:
    """Per-channel noise level at rest, used as the ZC/SSC threshold."""
    rest = x[labels == 0]
    if len(rest) == 0:
        raise ValueError("no rest samples (label 0) to measure noise from")
    return rest.std(axis=0)
