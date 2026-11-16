import numpy as np
import pytest

from emg.model import evaluate, make_lda


def test_lda_separates_clearly_different_gestures():
    rng = np.random.default_rng(0)
    centers = {0: 0.0, 6: 5.0, 13: 10.0}
    X, y, groups = [], [], []
    for label, c in centers.items():
        for rep in range(1, 7):
            X.append(rng.normal(c, 0.5, (20, 10)))
            y += [label] * 20
            groups += [rep] * 20
    X = np.vstack(X)
    pred = evaluate(make_lda(), X, np.array(y), np.array(groups))
    assert np.mean(pred == np.array(y)) > 0.95


def test_evaluate_needs_two_groups():
    with pytest.raises(ValueError):
        evaluate(make_lda(), np.zeros((10, 10)), np.zeros(10), np.ones(10))
