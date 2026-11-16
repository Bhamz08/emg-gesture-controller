import numpy as np
import pytest

from emg.features import features


def test_silent_signal_gives_all_zeros():
    window = np.zeros((200, 2))
    assert np.all(features(window, np.array([0.1, 0.1])) == 0)


def test_known_values_on_a_constant_signal():
    window = np.full((200, 1), -2.0)
    mav, rms, wl, zc, ssc = features(window, np.array([0.0]))
    assert mav == pytest.approx(2.0)
    assert rms == pytest.approx(2.0)
    assert wl == 0 and zc == 0 and ssc == 0


def test_zero_crossings_of_a_sine_wave():
    t = np.arange(1000) / 1000
    x = np.sin(2 * np.pi * 10 * t + 0.1)   # 10 Hz for 1 s: 20 crossings
    _, _, _, zc, _ = features(x[:, None], np.array([0.0]))
    assert zc == 20


def test_threshold_ignores_small_noise():
    rng = np.random.default_rng(0)
    noise = rng.normal(0, 0.01, (200, 1))
    _, _, _, zc, ssc = features(noise, np.array([1.0]))
    assert zc == 0 and ssc == 0


def test_features_come_channel_by_channel():
    window = np.column_stack([np.ones(200), 3 * np.ones(200)])
    f = features(window, np.array([0.0, 0.0]))
    assert len(f) == 10
    assert f[0] == pytest.approx(1.0) and f[5] == pytest.approx(3.0)


def test_mismatched_thresholds_fail_fast():
    with pytest.raises(ValueError):
        features(np.zeros((200, 2)), np.array([0.1]))
