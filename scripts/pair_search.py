"""Test every pair of Ninapro's 12 electrodes across subjects and rank them.

Each pair is scored on the same windows per subject, then averaged across subjects.
Choose a pair by its average AND its worst subject, not by one subject's best result.

Example:
    python scripts/pair_search.py data/ninapro/S1_E1_A1.mat data/ninapro/S2_E1_A1.mat ...
"""

import argparse
from itertools import combinations

import numpy as np

from emg import ninapro
from emg.config import GESTURES, NINAPRO_CHANNELS
from emg.model import evaluate, make_lda
from emg.signal import clean, rest_noise
from emg.windows import balance_rest, cut_windows

ALL = list(range(12))
PAIRS = list(combinations(ALL, 2))


def subject_scores(path) -> np.ndarray:
    """Accuracy of every pair for one subject, in PAIRS order."""
    emg, labels, reps = ninapro.load(path, ALL)
    emg = clean(emg)
    thresh = rest_noise(emg, labels)
    X_all, y, groups = cut_windows(emg, labels, reps, thresh, GESTURES)  # 60 features
    keep = balance_rest(y)
    X_all, y, groups = X_all[keep], y[keep], groups[keep]
    per_channel = X_all.reshape(len(y), 12, 5)  # features come channel by channel

    scores = []
    for a, b in PAIRS:
        X = per_channel[:, [a, b], :].reshape(len(y), 10)
        pred = evaluate(make_lda(), X, y, groups)
        scores.append(np.mean(pred == y))
    return np.array(scores)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("files", nargs="+", help="Ninapro DB2 .mat files, one per subject")
    p.add_argument("--top", type=int, default=10, help="how many pairs to show")
    args = p.parse_args()

    files = ninapro.expand(args.files)
    table = []
    for path in files:
        print(f"Scoring {ninapro.subject_name(path)}...")
        table.append(subject_scores(path))
    table = np.array(table)  # subjects x pairs

    avg = table.mean(axis=0)
    worst = table.min(axis=0)
    order = np.argsort(-avg)

    print(f"\nTop {args.top} pairs across {len(files)} subject(s) (electrode numbers from 1):")
    print(f"{'rank':>4}  {'pair':>7}  {'average':>8}  {'worst':>8}")
    for rank, i in enumerate(order[:args.top], start=1):
        a, b = PAIRS[i]
        print(f"{rank:>4}  {a + 1:>3} + {b + 1:<3}  {avg[i]:>8.1%}  {worst[i]:>8.1%}")

    chosen = PAIRS.index(tuple(NINAPRO_CHANNELS))
    rank = int(np.where(order == chosen)[0][0]) + 1
    print(f"\nCurrent choice, electrodes {NINAPRO_CHANNELS[0] + 1} + {NINAPRO_CHANNELS[1] + 1}: "
          f"average {avg[chosen]:.1%}, worst {worst[chosen]:.1%}, rank {rank} of {len(PAIRS)}")


if __name__ == "__main__":
    main()
