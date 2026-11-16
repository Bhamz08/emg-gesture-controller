import numpy as np
import pytest

from emg.signal import clean, rest_noise


def _power_at(x, freq, fs=1000):
    spectrum = np.abs(np.fft.rfft(x))
    freqs = np.fft.rfftfreq(len(x), 1 / fs)
    return spectrum[np.argmin(np.abs(freqs - freq))]


def test_notch_removes_60_hz_but_keeps_muscle_band():
    t = np.arange(5000) / 1000
    x = np.sin(2 * np.pi * 60 * t) + np.sin(2 * np.pi * 150 * t)
    y = clean(x[:, None])[1000:, 0]          # skip the filter's settling time
    assert _power_at(y, 60) < 0.05 * _power_at(y, 150)


def test_high_pass_removes_drift():
    x = np.full((5000, 1), 2.0)              # constant offset, like a sensor's midpoint
    y = clean(x)
    assert abs(y[2000:].mean()) < 0.01


def test_clean_rejects_1d_input():
    with pytest.raises(ValueError):
        clean(np.zeros(100))


def test_rest_noise_needs_rest_samples():
    with pytest.raises(ValueError):
        rest_noise(np.zeros((10, 2)), np.full(10, 6))
