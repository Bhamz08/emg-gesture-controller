"""Models and honest evaluation."""

import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def make_lda():
    return make_pipeline(StandardScaler(), LinearDiscriminantAnalysis())


def make_random_forest():
    return make_pipeline(StandardScaler(), RandomForestClassifier(n_estimators=200, random_state=0))


def evaluate(model, X, y, groups) -> np.ndarray:
    """Predict every window with a model that never saw its repetition.

    Holds out one repetition at a time. A random split would leak nearly identical
    neighboring windows into training and make accuracy look too good.
    """
    n_groups = len(np.unique(groups))
    if n_groups < 2:
        raise ValueError("need at least 2 repetition groups to evaluate")
    return cross_val_predict(model, X, y, groups=groups, cv=GroupKFold(n_splits=n_groups))
