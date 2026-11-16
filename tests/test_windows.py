import numpy as np

from emg.ninapro import fix_rest_reps
from emg.windows import balance_rest, cut_windows, window_ends


def test_windows_skip_gesture_changes_and_unused_gestures():
    labels = np.array([0] * 400 + [6] * 400 + [99] * 400)
    ends = window_ends(labels, {0: "rest", 6: "fist"}, win=200, step=50)
    for e in ends:
        lab = labels[e - 200:e]
        assert lab.min() == lab.max()
        assert lab[0] in (0, 6)
    assert 99 not in labels[ends - 1]


def test_cut_windows_labels_and_groups_match_window_end():
    n = 1200
    emg = np.random.default_rng(0).normal(size=(n, 2))
    labels = np.array([0] * 600 + [6] * 600)
    reps = np.array([1] * 600 + [2] * 600)
    X, y, groups = cut_windows(emg, labels, reps, np.array([0.1, 0.1]), {0: "rest", 6: "fist"})
    assert X.shape[1] == 10
    assert set(zip(y, groups)) == {(0, 1), (6, 2)}


def test_balance_rest_caps_rest_at_biggest_gesture():
    y = np.array([0] * 100 + [6] * 30 + [13] * 40)
    keep = balance_rest(y)
    assert (y[keep] == 0).sum() == 40
    assert (y[keep] == 6).sum() == 30


def test_rest_takes_previous_repetition_and_leading_rest_gets_first():
    reps = np.array([0, 0, 1, 1, 0, 0, 2, 0])
    assert list(fix_rest_reps(reps)) == [1, 1, 1, 1, 1, 1, 2, 2]
