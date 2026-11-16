"""Features: 5 numbers per channel that describe one window of EMG."""

import numpy as np


def features(window: np.ndarray, thresh: np.ndarray) -> np.ndarray:
    """Return [MAV, RMS, WL, ZC, SSC] for each channel, channel by channel.

    window: (samples x channels), already cleaned.
    thresh: per-channel noise level; ZC and SSC ignore changes smaller than this.
    """
    if window.ndim != 2:
        raise ValueError(f"expected (samples x channels), got shape {window.shape}")
    if len(thresh) != window.shape[1]:
        raise ValueError(f"{window.shape[1]} channels but {len(thresh)} thresholds")

    out = []
    for c in range(window.shape[1]):
        x = window[:, c]
        d = np.diff(x)
        t = thresh[c]
        mav = np.mean(np.abs(x))                                   # how hard the muscle works
        rms = np.sqrt(np.mean(x ** 2))                             # same, weights spikes more
        wl = np.sum(np.abs(d))                                     # how jagged the signal is
        zc = np.sum((x[:-1] * x[1:] < 0) & (np.abs(d) >= t))       # zero crossings
        ssc = np.sum((d[:-1] * d[1:] < 0) &
                     ((np.abs(d[:-1]) >= t) | (np.abs(d[1:]) >= t)))  # slope sign changes
        out += [mav, rms, wl, zc, ssc]
    return np.array(out, dtype=float)
